---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Getting started with Fantasy Premier League 2021/2022

This is a introduction to the ongoing data scarping of online game [Fantasy Premier League](https://fantasy.premierleague.com/ )

In particular this notebook gives an bried introduction to how to:
* Download gathered data
* Explore gathered data
* Analyze gathered data

The goal is

Have fun!

```python
# Installerer pakke for å blant annet laste ned data.
!pip install -q git+https://github.com/martgra/fpl2021.git
```

## Getting the data
The data available is stored in Azure Blobs every 6 hours by dumping data from https://fantasy.premierleague.com/api/bootstrap-static/. This means that data for 2021/22 season is continously being added to.

The data is being made available in two separate containers:
* 2020/21 data --> https://martinfplstats1337.blob.core.windows.net/2020-fpl-data?restype=container&comp=list
* 2021/22 data --> https://martinfplstats1337.blob.core.windows.net/2021-fpl-data?restype=container&comp=list

In this section we download the stored data to our local machine.

```python
# Paths to store data from 2020-season and 2021 season respectively.
DATA_2020 = "../data/raw/2020-fpl-data"
DATA_2021 = "../data/raw/2021-fpl-data"

!fantasy storage download-all -d {DATA_2020}

# This command can be rerun periodically to download new data dumps.
!fantasy storage --container 2021-fpl-data download-all -d {DATA_2021}

# Print content of raw data dir
!ls ../data/raw
```

## Quick and dirty look at our data
In this section we have a quick look at the data that we have downloaded. Basically these are "snapshots" of the FPL fantasy game at a given moment. Hopefully this will be useful to us :-)

```python
import json
from fpl.data.io import list_data_dir

# We grab a sample from the middle of the 2020 dataset
sample_2020 = list_data_dir(DATA_2020)[len(list_data_dir(DATA_2020))//2]

# ...and look at its content
with open(sample_2020) as file:
   sample = json.load(file)

print(list(sample.keys()))
```

### Hold on - thats a lot of data. Lets look at the interesting ones!
Out of the "keys" in our selected sample it seems like the three most interesting entities are:
* elements - holding stats and metadata about each player
* teams - holding stats and metadata about each team
* events - holding metadata about each gameweek
* download_time - the time the dump was made

```python
# Loading events to have closer look
events_sample = sample["events"]
print(json.dumps(events_sample[0], indent=4))
```

```python
# Loading teams to have closer look
teams_sample = sample["teams"]
print(json.dumps(teams_sample[0], indent=4))
```

```python
# Loading elements to have closer look
elements_sample = sample["elements"]
print(json.dumps(elements_sample[0], indent=4, ensure_ascii=False))
```

<!-- #region -->
### Introduction to elements - the most interesting data we have.
Elements is by far the most interesting "entitiy" in the dataset, holding lots of information about each player.


To give a head start check out the file ```data_description/data_description.json``` found in the repo!
It holds my personal notes regarding each element attribute and can be utilized like this:
<!-- #endregion -->

```python
with open("../data_description/data_description.json") as file:
    element_desc = json.load(file)

# We print the description for an attribute we are curious about, in this case "ict_index"
print(json.dumps(element_desc["elements"]["ict_index"], indent=4, ensure_ascii=False))
```

## Using the gathered data :-)


### Converting to CSV
From the previous part we assume that the most interesting data are stored in "elements". For a more handy format we extract all data elements and store them in one big CSV. We also store the gameweek AND the download-time of each data dump.

```python
# Paths to transformed CSV from 2020-season and 2021 season respectively.
DATA_2020_CSV = "../data/transformed/data2020.csv"
DATA_2021_CSV = "../data/transformed/data2021.csv"

# Compiling a CSV holding all "elements". Timestamp and gameweek is added.
!fantasy storage to-csv --data-dir {DATA_2020} --save {DATA_2020_CSV}
!fantasy storage to-csv --data-dir {DATA_2021} --save {DATA_2021_CSV}

# Printing content of transformed data.
!ls ../data/transformed
```

### Creating some insight from our actual data in Pandas

To demonstrate how to load and use the data we do a very basic comparison of the highest scoring players during the 2020-2021 season. We compare their average points output.

```python
# Importing pandas and loading data from CSV to dataframe.

import pandas as pd
df_2020 = pd.read_csv(DATA_2020_CSV)
```

```python
# We select the last record of points scored by each player for each gameweek
df_points = df_2020.groupby(["player_id", "gameweek"], as_index=False)[["event_points", "web_name", "minutes"]].last()

# We also select the top10 players with the MOST points in our last download
last_download = df_2020["download_time"].tolist()[-1]
highest_score_players = df_2020[df_2020["download_time"] == last_download].sort_values(by=['total_points'], ascending=False).head(10)[["web_name", "player_id", "total_points"]]


highest_score_players
```

```python
# We create a DF holding data regarding these players.
df_points = df_points[df_points["player_id"].isin(highest_score_players["player_id"])]
```

```python
# Based on the selected players we plot their "average points score" and "standard deviation".

import seaborn as sns
import matplotlib.pyplot as plt
sns.set(rc = {'figure.figsize':(15,8)})
sns.set_theme(style="darkgrid")
ax = sns.pointplot(x="web_name", y="event_points", data=df_points, join=False)
```

## Going forward

The dataset is really collected with time series in mind. However - some interesting insight CAN be obtained looking at this data. My best tip is **having fun** and being **curious**. Here are some tips for the road:

**API - Other useful methods**
* Fixtures: https://fantasy.premierleague.com/api/fixtures/
* Get the history of a FPL-participant: https://fantasy.premierleague.com/api/entry/{}/history/
* Participant score: https://fantasy.premierleague.com/api/entry/{team-id}/
* Score in a particular "classic"-league: https://fantasy.premierleague.com/api/leagues-classic/{league-id}/standings/
* Score in  a particular "H2H"-league: https://fantasy.premierleague.com/api/leagues-h2h/{league-id}/standings/
* Latest transfers: https://fantasy.premierleague.com/api/entry/{team-id}/transfers-latest/
* My Team https://fantasy.premierleague.com/api/my-team/{team-id}/
To use "my team api" authentication is required https://medium.com/@bram.vanherle1/fantasy-premier-league-api-authentication-guide-2f7aeb2382e4)

**Other useful data sources**
* Odds-api: https://the-odds-api.com/

**Other useful links**
* Reddit-thread about FPL API https://www.reddit.com/r/FantasyPL/comments/c64rrx/fpl_api_url_has_been_changed/
* Blogpost about FPL API (drf needs to be changed to api) https://medium.com/@YourMumSaysWhat/how-to-get-data-from-the-fantasy-premier-league-api-4477d6a334c3
Historic data for FPL https://github.com/vaastav/Fantasy-Premier-League
