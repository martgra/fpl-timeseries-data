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

```python
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

from fpl.data.transformations import to_csv, _nearest
```

### Loading teams CSV

```python
teams_2020_df = pd.read_csv("../data/transformed/teams_2020.csv")
teams_2021_df = pd.read_csv("../data/transformed/teams_2021.csv")
teams_2021_df.head(1)
```

### Loading elements CSV

```python
elements_2020_df = pd.read_csv("../data/transformed/elements_2020.csv")
elements_2021_df = pd.read_csv("../data/transformed/elements_2021.csv")
```

### Grouping elements and teams on unique identifier and gameweek

```python
def group_join_element_teams(elements_df, teams_df):    
    elements_df = elements_df.groupby(["code", "gameweek"], as_index=False).last()
    teams_df = teams_df.groupby(["id", "gameweek"], as_index=False).last()
    elements_df = elements_df.join(teams_df.set_index(["id", "gameweek"]), on=["team", "gameweek"], rsuffix="_team")
    return elements_df
```

```python
elements_grouped_2020 = group_join_element_teams(elements_2020_df, teams_2020_df)
elements_grouped_2021 = group_join_element_teams(elements_2021_df, teams_2021_df)
```

```python
def merge_years(years_df_list):
    years_df_list[0].loc[:, "season"] = 0
    for i, df in enumerate(years_df_list[1:]):
        df.loc[:, "season"] = i + 1 
        try:
            assert df.columns.tolist() == years_df_list[0].columns.tolist()
        except:
            print([i for i in df.columns.tolist() if i not in years_df_list[0].columns.tolist()])
            print([i for i in  years_df_list[0].columns.tolist() if i not in df.columns.tolist()])
        years_df_list = years_df_list[0].append(df, ignore_index=True)
    return years_df_list
```

```python
merged_df = merge_years([elements_grouped_2020, elements_grouped_2021])
```

### Bucketizing minutes and adding previos 5 matches

```python
def fix_minutes(df):
    df.loc[df.gameweek == 0, "minutes"] = df.loc[df.gameweek == 0, "minutes"]/38
    df.loc[df.gameweek == 0, "minutes"] = df.loc[df.gameweek == 0, "minutes"].map(lambda x: x//15)
    
    for season in df.season.unique().tolist():
        for player in df.code.unique().tolist(): 
            df.loc[(df.code == player) & (df.season == season) & (df.gameweek > 0), "minutes"] = df[(df.code == player) & (df.season == season) & (df.gameweek > 0)]["minutes"].diff().fillna(df[(df.code == player) & (df.season == season)  & (df.gameweek > 0)]["minutes"])
            df.loc[(df.code == player) & (df.season == season) & (df.gameweek > 0), "minutes"] = df[(df.code == player) & (df.season == season) & (df.gameweek > 0)]["minutes"].map(lambda x: x//15)
            for i in range(1,5):
                df.loc[df.code == player, f"minutes_{i}"] = df.loc[df.code == player, "minutes"].shift(i).fillna(-1)
                df.loc[df.code == player, f"event_points_{i}"] = df.loc[df.code == player, "event_points"].shift(i).fillna(-1)
    return df
```

```python
merged_df = fix_minutes(merged_df)

```

### Exploring "chance_of_playing_..."

```python
merged_df["chance_of_playing_this_round"].value_counts(dropna=False)
```

```python
merged_df["chance_of_playing_next_round"].value_counts(dropna=False)
```

### Filling NaN's in chance of playing

```python
def fill_chance_playing(df):
    df["chance_of_playing_next_round"] = df["chance_of_playing_next_round"].fillna(100.0)
    df["chance_of_playing_this_round"] = df["chance_of_playing_this_round"].fillna(100.0)
    return df
```

```python
merged_df = fill_chance_playing(merged_df)
```

### Transfers in/out as percentage

```python
def _get_data_file_by_download(download_time):
    date = datetime.strptime(download_time, "%Y-%m-%d %H:%M:%S.%f")
    for dir in  [i for i in Path("../data/raw").iterdir() if "fpl-data" in i.name]:
        # Handling mismatch between download-time in file and filename.
        file = [file for file in dir.iterdir() if date.strftime("%y-%m-%d") in file.name]
        if file:
            return _nearest(file, download_time)
    
def _get_total_players(file_path):
    with open(file_path) as file:
        return json.load(file)["total_players"]

def fix_transfers_gw_0(df):
    gw_0_map = {i: _get_total_players(_get_data_file_by_download(i)) for i in  df[df.gameweek == 0].download_time.unique()}
    df.loc[df.gameweek == 0, "transfers_in_event"] = df.loc[df.gameweek == 0].apply(lambda x: gw_0_map[x.download_time] * (x.selected_by_percent/100),axis=1).astype("int32")
    return df
```

```python
def transfers_in_out(df):
    df = fix_transfers_gw_0(df)
    _num_transfers = df[["gameweek", "transfers_in_event", "transfers_out_event"]].groupby(["gameweek"]).sum()
    df = df.join(_num_transfers, on=["gameweek"], rsuffix="_total")
    df["transfers_in_event"] = df.apply(lambda x: x["transfers_in_event"] / x["transfers_in_event_total"] if x["transfers_in_event_total"] > 0 else 0, axis=1 )
    df["transfers_out_event"] = df.apply(lambda x: x["transfers_out_event"] / x["transfers_out_event_total"] if x["transfers_out_event_total"] > 0 else 0, axis=1 )
    return df
```

```python
merged_df = transfers_in_out(merged_df)
```

### Adding target value

```python
def add_target_value(df):
    df.loc[::-1,"target"] = df.iloc[::-1].groupby('code').event_points.apply(lambda x: x.rolling(min_periods=1, window=5).sum().shift(1))
    return df
```

```python
merged_df = add_target_value(merged_df)
```

```python
merged_df[merged_df.web_name=="Salah"]
```

### Columns to drop

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
sns.set_theme(style="white")

# Compute the correlation matrix
corr = merged_df.corr()
corr = corr.applymap(lambda x: x if abs(x) > 0.10 and abs(x) != 1.0 else 0)
# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(33, 27))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1.0, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
```

```python
merged_df.corr()["target"].sort_values()
```

```python
[i for i in merged_df.columns.tolist() if "rank" in i]
```

```python
def drop_columns(df, list_of_lists):
    return df.drop([j for i in list_of_lists for j in i],axis=1, errors="ignore")
    
```

```python
merged_df = drop_columns(merged_df, drop_colums)

```

```python
print(len(merged_df.columns.tolist()))
print(len(elements_grouped_2021.columns.tolist()))

```

```python
corr = merged_df.corr()

mask = np.triu(np.ones_like(corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(33, 27))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1.0, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
```

### Exploring NaNs

```python
merged_df.columns[merged_df.isna().any()].tolist()
```

### Fixing NaN and reducing rank in set piece orders

```python
def bucket_setpieces(df):
    df["penalties_order"] = df["penalties_order"].map(lambda x: 3 if (x != x) or (x > 2) else x)
    df["direct_freekicks_order"] = df["direct_freekicks_order"].map(lambda x: 3 if (x != x) or (x > 2) else x)
    df["corners_and_indirect_freekicks_order"] = merged_df["corners_and_indirect_freekicks_order"].map(lambda x: 3 if (x != x) or (x > 2) else x)
    return df
```

```python
merged_df = bucket_setpieces(merged_df)
```

### Filling opponent information NaNs

```python
merged_df[[i for i in merged_df.columns[merged_df.isna().any()].tolist() if "opponent" in i]] = merged_df[[i for i in merged_df.columns[merged_df.isna().any()].tolist() if "opponent" in i]].fillna(-1)
```

```python
merged_df["target"]
```

### Handeling gw_flag

```python
def played_in_gameweek(df):
    df[[i for i in df.columns.tolist() if "played_in_gw" in i]] = df[[i for i in df.columns.tolist() if "played_in_gw" in i]].applymap(lambda x: 1 if x > 0 else 0)
    return df
```

```python
merged_df = played_in_gameweek(merged_df)
```

```python
pd.set_option("display.max_columns", None)
described = merged_df.describe().loc[["mean", "std", "min", "max"]][merged_df.describe().loc[["mean", "std", "min", "max"]] < 1500].dropna(axis=1)
described.T
```

```python
max_values = described.T[(described.T["max"] > described.T["mean"] + described.T["std"] * 2)]
max_values
```

```python
def rolling_seasons(df):
    
    with open("../data_description/data_description.json") as file:
        columns_desc = json.load(file)
    cummulative_columns = [i for i,y in columns_desc["elements"].items() if y["calculated"] == "cumulative_sum" and i in df.columns.tolist() and "minutes" not in i]
    
    df.loc[(df.gameweek == 0) & (df.season == 0), cummulative_columns] = round(df.loc[(df.gameweek == 0) & (df.season == 0), cummulative_columns] / 38)
    for season in df.season.unique().tolist()[1:]:
        print(season)
        #df.loc[(df.gameweek == 0) & (df.season == season), cummulative_columns] = 
        return df.loc[(df.gameweek == 38) & (df.season == season-1) & (df.web_name.isin(df[df.season == season-1].web_name)), cummulative_columns]
```

```python
rolling_seasons(merged_df)[(merged_df.web_name=="Salah") & (merged_df.gameweek == 0)]
```

```python
[i for i,y in columns_desc["elements"].items() if y["calculated"] == "cumulative_sum"]
```

```python
descriptives = ["Unnamed: 0", "squad_number", "news", "first_name", "news_added", "photo", "second_name", "special",
                "squad_number", "corners_and_indirect_freekicks_text", "direct_freekicks_text", "penalties_text", 
                "download_time", "Unnamed: 0_team", 'pulse_id']
unique_identifiers = ["team", "team_code", "player_id", "id", "code_team"]
high_internal_corr = ['value_season','value_form','influence_rank', 'creativity_rank', 'threat_rank', 'ict_index_rank', "total_points", "bonus"]
little_information = ['in_dreamteam', "own_goals", "penalties_missed", "red_cards", "win", "unavailable", "team_division", 
                     "short_name", "position", "points", "played", "name", "loss", "form_team", "draw", "transfers_in_event_total", "transfers_out_event_total"]
categorical = ["element_type", "status"]
for_engineering = ["penalties_order", "direct_freekicks_order", "corners_and_indirect_freekicks_order",  
                   "cost_change_event", "cost_change_event_fall", "cost_change_start", "cost_change_start_fall" , 
                   "dreamteam_count", "transfers_in_event", "transfers_in", "transfers_out", "transfers_out_event",
                  "goals_scored", "assists", "clean_sheets", "goals_conceded", "penalties_saved", "yellow_cards", "saves", "bps",
                  ]

drop_colums = [descriptives, unique_identifiers, high_internal_corr, little_information]

```

```python
import json

with open("../data_description/data_description.json") as file:
    data_desc = json.load(file)
    
    
[i for i,y in data_desc["elements"].items() if y["type"] == "descriptive"]
    
# for i,y in data_desc["teams"].items():
#     if i in descriptives:
#         y.update({"feature_engineering": {"action": "dropp", "feature_notes": "None"}})

for i,y in data_desc["elements"].items():
    if i in descriptives:
        y.update({"feature_engineering": {"action": "drop", "feature_notes": "No information"}})


```

```python
with open("../data_description/data_description.json", "w") as file:
    json.dump(data_desc,file, ensure_ascii=False, indent=4)
```

```python

```

```python

```
