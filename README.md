# **Fantasy Premier League Time series data**

Inspired by the following tutorial:
https://towardsdatascience.com/fantasy-premier-league-value-analysis-python-tutorial-using-the-fpl-api-8031edfe9910


## **Getting started**

### **Install package to get all the data**
To download the full raw dataset run the following code. 
```bash
# Install the FPL package
pip install git+https://github.com/martgra/fpl-timeseries-data.git

# Download all new data for season 2020 and 2021
fantasy storage --container 2021-fpl-data download-all
fantasy storage --container 2021-fpl-data download-all

# Extract elements from each JSON and store as CSV 
fantasy storage to-csv --data_dir data/raw/2020-fpl-data --save transformed_2020.csv
fantasy storage to-csv --data_dir data/raw/2021-fpl-data --save transformed_2021.csv
```

### **A brief introduction to the repo**
In this brief introduction we're gonna open the jupyter notebook [GETTING_STARTED.md](notebooks/GETTING_STARTED.md). To use this notebook it is recommended to follow the steps listed below. The notebook will go through
1. How to get the data
2. A brief introduction to the dataset and its content
3. Using the data for analytic purposes

```bash
# Clone and open repo
git clone https://github.com/martgra/fpl-timeseries-data.git && cd fpl-timeseries-data.git

# Create virtual environment (optional, recommended)
python3 -m venv venv && source venv/bin/activate && python -m pip install --upgrade pip

# Install development requirements and package. 
pip install -r requirements_dev.txt
pip install -e .

# Start jupyter
jupyter notebook --notebook-dir=notebooks
```

## **Some considerations about the Dataset**

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
I have made some notes regarding the data in "elements". These notes can be found here: [data_description/data_description.json](data_description/data_description.json). It is strongly recommended to review these notes and make own assumptions and notes.  

## **A time series problem**
Allthough FPL data has plenty of usages, this data has been specifically collected with [timeseries](https://en.wikipedia.org/wiki/Time_series) in mind. 

<div class="flourish-embed flourish-bar-chart-race" data-src="visualisation/6906400"><script src="https://public.flourish.studio/resources/embed.js"></script></div>


## **Other useful stuff**
### **API - Other useful methods**

- Fixtures: https://fantasy.premierleague.com/api/fixtures/
- A single teams hostory: https://fantasy.premierleague.com/api/entry/{}/history/
- A single teams score: https://fantasy.premierleague.com/api/entry/{team-id}/
- Score in a specific "classic"-league: https://fantasy.premierleague.com/api/leagues-classic/{league-id}/standings/
- Score in a specific "H2H"-league: https://fantasy.premierleague.com/api/leagues-h2h/{league-id}/standings/
- Latest transfers: https://fantasy.premierleague.com/api/entry/{team-id}/transfers-latest/
- My Team https://fantasy.premierleague.com/api/my-team/{team-id}/ \*

\*To use the "my team api" authentication is required. See following link
https://medium.com/@bram.vanherle1/fantasy-premier-league-api-authentication-guide-2f7aeb2382e4)

### **Other useful data sources**
There is plenty of data available for the English Premier League. One could for example look at match odds to get a better understanding of expected results or look into sosial media to create player and match sentiment analysis. 
* [The odds API to gather match odds](https://the-odds-api.com/)
* [Twitter API to analyze sosial media trends](https://developer.twitter.com/en/docs)

### **Other useful links**

- Reddit-thread about FPL API
  https://www.reddit.com/r/FantasyPL/comments/c64rrx/fpl_api_url_has_been_changed/
- Blogpost about FPL API (its a little old, but change drf with api and it seems to work)
  https://medium.com/@YourMumSaysWhat/how-to-get-data-from-the-fantasy-premier-league-api-4477d6a334c3
- Historic data for the FPL
  https://github.com/vaastav/Fantasy-Premier-League
- [Can maths tell us how to win at Fantasy Football? - Guest lecture at Oxford by Joshua Bull](https://www.youtube.com/watch?v=LzEuweGrHvc&t=943s)
