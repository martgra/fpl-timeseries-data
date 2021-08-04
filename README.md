# Fantasy Premier League Time series data

Inspired by the following tutorial:
https://towardsdatascience.com/fantasy-premier-league-value-analysis-python-tutorial-using-the-fpl-api-8031edfe9910


### **Getting started**

The repo is based in python3 and jupyter with jupytext for agile version control.

#### **Install package just to get data**

```bash
# Install the FPL package
$ pip install git+https://github.com/martgra/fpl-timeseries-data.git

# Download all new data for season 2020 and 2021
$ fantasy storage --container 2021-fpl-data download-all
$ fantasy storage --container 2021-fpl-data download-all

# Extract elements from each JSON and store as CSV 
$ fantasy storage to-csv --data_dir data/raw/2020-fpl-data --save transformed_2020.csv
$ fantasy storage to-csv --data_dir data/raw/2021-fpl-data --save transformed_2021.csv
```

#### **Development**
```bash
# Clone Repo
$ git clone https://github.com/martgra/fpl-timeseries-data.git
$ cd fpl-timeseries-data.git

# Create virtual environment (optional, recommended)
$ python3 -m venv venv && source venv/bin/activate
$ python -m pip install --upgrade pip

# Install development requirements and package. 
$ pip install -r requirements_dev.txt
$ pip install -e .
```

### Dataset

The dataset from Fantasy Premier League is accessed by folling this link.
https://fantasy.premierleague.com/api/bootstrap-static/

As of now the dataset is downloaded every 6th hour (UTC) and stored as as Azure blob "snapshot".

```python
{
    "events": [...],
    "game_settings": {...}, 
    "teams": [...], 
    "total_players": int,
    "element_stats": [...],
    "element_types": [...],
    "download_time": timestamp
}
```
**Description of the data** can be found here: [data_description/data_description.json](data_description/data_description.json).


API - Other useful methods

- Fixtures: https://fantasy.premierleague.com/api/fixtures/
- A single teams hostory: https://fantasy.premierleague.com/api/entry/{}/history/
- A single teams score: https://fantasy.premierleague.com/api/entry/{team-id}/
- Score in a specific "classic"-league: https://fantasy.premierleague.com/api/leagues-classic/{league-id}/standings/
- Score in a specific "H2H"-league: https://fantasy.premierleague.com/api/leagues-h2h/{league-id}/standings/
- Latest transfers: https://fantasy.premierleague.com/api/entry/{team-id}/transfers-latest/
- My Team https://fantasy.premierleague.com/api/my-team/{team-id}/ \*

\*To use the "my team api" authentication is required. See following link
https://medium.com/@bram.vanherle1/fantasy-premier-league-api-authentication-guide-2f7aeb2382e4)

### Other useful links

- Reddit-thread about FPL API
  https://www.reddit.com/r/FantasyPL/comments/c64rrx/fpl_api_url_has_been_changed/
- Blogpost about FPL API (its a little old, but change drf with api and it seems to work)
  https://medium.com/@YourMumSaysWhat/how-to-get-data-from-the-fantasy-premier-league-api-4477d6a334c3
- Historic data for the FPL
  https://github.com/vaastav/Fantasy-Premier-League
