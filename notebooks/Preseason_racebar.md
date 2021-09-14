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

# Racebar of transfers

We want to make a "racebar chart" of transfers, showing the most popular players. The visualization is done in [Flourish](https://app.flourish.studio/login). To be able to do this we need to wrangle our data a little.

```python
import os
from pathlib import Path
import json

import pandas as pd

from fpl.data.io import list_data_dir
```

```python
# Assuming that we have transformed 2021 data to CSV we load this data.

DATA2021 = "../data/transformed/transformed_2021.csv"
data2021 = pd.read_csv(DATA2021, index_col=0)
```

### Estimating number of transfers

As transfers are revield after the first gameweek starts we try to estimate the incomming transfers based _selected_by_percent_ and _total_players_. _selected_players_ is found in the .CSV. However to obtain total_players we need to revisit the raw data. 

```python
# Getting the list of all data dumps from 2021 season
raw_data = list_data_dir("../data/raw/2021-fpl-data/")


# We iterate through all dumps and select a list of tuples with (download_time, total_players)
num_players = []
for i in raw_data:
    with open(i) as file:
        data = json.load(file)
        num_players.append((data["download_time"],data["total_players"]))

# From the list of download_time and total_players we create a new dataframe. 
num_players = pd.DataFrame(num_players)
num_players.columns = ["download_time", "total_players"]

# We join the number_players dataframe with our existing one 
data2021 = data2021.join(num_players.set_index('download_time'), on='download_time')
```

```python
# We select the required columns and store them in a new dataframe. 
df_selected = data2021[["web_name", "team","selected_by_percent", "total_players", "download_time"]].copy()

# We create a new feature "total_transfers" by multiplying "selected_by_precentage" and "total_players"
df_selected["total_transfers"] = (df_selected["total_players"] * (df_selected["selected_by_percent"]/100)).astype("int32")
```

```python
# We use pandas.pivot_table to have Names as index, download_time as columns and values as the total transfers. 
racebar_df = df_selected[["web_name","download_time","total_transfers"]]
racebar_df = pd.pivot_table(racebar_df, index="web_name", columns="download_time", values="total_transfers")

# The transformed dataframe is stored in our project root. 
racebar_df.to_csv(Path("../net_transfer.csv"))
```

```python
racebar_df
```

```python

```
