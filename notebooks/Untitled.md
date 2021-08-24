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

from fpl.data.transformations import to_csv
```

### Loading teams CSV

```python
teams_2021_df = pd.read_csv("../data/transformed/transformed.csv")
teams_2021_df.head(1)
```

### Loading elements CSV

```python
elements_2021_df = pd.read_csv("../data/transformed/transformed_2020.csv")
elements_2021_df.head(1)
```

### Grouping elements and teams on unique identifier and gameweek

```python
elements_grouped = elements_2021_df.groupby(["code", "gameweek"], as_index=False).last()
teams_2021_df_grouped = teams_2021_df.groupby(["id", "gameweek"], as_index=False).last()
```

```python
elements_grouped = elements_grouped.join(teams_2021_df_grouped.set_index(["id", "gameweek"]), on=["team", "gameweek"], rsuffix="_team")
```

### Bucketizing minutes and adding previos 5 matches

```python
elements_grouped.loc[elements_grouped.gameweek == 0, "minutes"] = elements_grouped.loc[elements_grouped.gameweek == 0, "minutes"]/38
elements_grouped.loc[(elements_grouped.web_name == "Salah") & (elements_grouped.gameweek > 0), "minutes"] = elements_grouped[(elements_grouped.web_name == "Salah") & (elements_grouped.gameweek > 0)]["minutes"].diff().fillna(elements_grouped[(elements_grouped.web_name == "Salah")  & (elements_grouped.gameweek > 0)]["minutes"])

for player in elements_grouped.code.unique().tolist(): 
    for i in range(1,5):
        elements_grouped.loc[elements_grouped.code == player, f"minutes_{i}"] = elements_grouped[elements_grouped.code == player]["minutes"].map(lambda x: x//15).shift(i).fillna(-1)
        elements_grouped.loc[elements_grouped.code == player, f"event_points_{i}"] = elements_grouped[elements_grouped.code == player]["event_points"].shift(i).fillna(-1)

```

### Exploring "chance_of_playing_..."

```python
elements_grouped["chance_of_playing_this_round"].value_counts(dropna=False)
```

```python
elements_grouped["chance_of_playing_next_round"].value_counts(dropna=False)
```

### Filling NaN's in chance of playing

```python
elements_grouped["chance_of_playing_next_round"] = elements_grouped["chance_of_playing_next_round"].fillna(100.0)
elements_grouped["chance_of_playing_this_round"] = elements_grouped["chance_of_playing_this_round"].fillna(100.0)
```

### Transfers in/out as percentage

```python
num_transfers = elements_grouped[["gameweek", "transfers_in_event", "transfers_out_event"]].groupby(["gameweek"]).sum()
new_element = elements_grouped.join(num_transfers, on=["gameweek"], rsuffix="_total")
new_element["transfers_in_event"] = new_element.apply(lambda x: x["transfers_in_event"] / x["transfers_in_event_total"] if x["transfers_in_event_total"] > 0 else 0, axis=1 )
new_element["transfers_out_event"] = new_element.apply(lambda x: x["transfers_out_event"] / x["transfers_out_event_total"] if x["transfers_out_event_total"] > 0 else 0, axis=1 )
```

### Adding target value

```python
new_element.loc[::-1,"target"] = new_element.iloc[::-1].groupby('code').event_points.apply(lambda x: x.rolling(min_periods=1, window=5).sum().shift(1))
```

### Columns to drop

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
sns.set_theme(style="white")

# Compute the correlation matrix
corr = new_element.corr()
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
new_element.corr()["target"].sort_values()["draw"]
```

```python
[i for i in new_element.columns.tolist() if "rank" in i]
```

```python
descriptives = ["Unnamed: 0", "squad_number", "news", "first_name", "news_added", "photo", "second_name", "special",
                "squad_number", "corners_and_indirect_freekicks_text", "direct_freekicks_text", "penalties_text", 
                "download_time", "Unnamed: 0_team", 'pulse_id']
unique_identifiers = ["team", "team_code", "player_id", "id", "code_team"]
high_internal_corr = ['value_season','value_form','influence_rank', 'creativity_rank', 'threat_rank', 'ict_index_rank', "total_points", "bonus"]
little_information = ['in_dreamteam', "own_goals", "penalties_missed", "red_cards", "win", "unavailable", "team_division", 
                     "short_name", "position", "points", "played", "name", "loss", "form_team", "draw", ]
categorical = ["element_type", "status"]
for_engineering = ["penalties_order", "direct_freekicks_order", "corners_and_indirect_freekicks_order",  
                   "cost_change_event", "cost_change_event_fall", "cost_change_start", "cost_change_start_fall" , 
                   "dreamteam_count", "transfers_in_event", "transfers_in", "transfers_out", "transfers_out_event",
                  "goals_scored", "assists", "clean_sheets", "goals_conceded", "penalties_saved", "yellow_cards", "saves", "bps",
                  ]



```

```python
for i in [i for i in new_element.columns.tolist() if i not in descriptives + unique_identifiers + high_internal_corr + little_information + categorical + unfair_info + for_engineering]:
    print(i)
    try:
        print(new_element.corr()["target"][i])
    except:
        pass
    input()
```

```python
selected_elements.columns.tolist()


```

```python
corr = selected_elements.corr()

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
selected_elements.columns[selected_elements.isna().any()].tolist()
```

### Fixing NaN and reducing rank in set piece orders

```python
selected_elements = new_element.drop(descriptives + unique_identifiers + high_internal_corr + little_information, axis=1)
selected_elements["penalties_order"] = selected_elements["penalties_order"].map(lambda x: 3 if (x != x) or (x > 2) else x)
selected_elements["direct_freekicks_order"] = selected_elements["direct_freekicks_order"].map(lambda x: 3 if (x != x) or (x > 2) else x)
selected_elements["corners_and_indirect_freekicks_order"] = selected_elements["corners_and_indirect_freekicks_order"].map(lambda x: 3 if (x != x) or (x > 2) else x)
```

```python
selected_elements["penalties_order"].value_counts()
```

```python
selected_elements["direct_freekicks_order"].value_counts()
```

```python
selected_elements["corners_and_indirect_freekicks_order"].value_counts()
```

### Filling opponent information NaNs

```python
selected_elements[[i for i in selected_elements.columns[selected_elements.isna().any()].tolist() if "opponent" in i]] = selected_elements[[i for i in selected_elements.columns[selected_elements.isna().any()].tolist() if "opponent" in i]].fillna(-1)
```

### Handeling gw_flag

```python
selected_elements[[i for i in selected_elements.columns.tolist() if "played_in_gw" in i]] = selected_elements[[i for i in selected_elements.columns.tolist() if "played_in_gw" in i]].applymap(lambda x: 1 if x > 0 else 0)
```

```python
data = sorted(selected_elements.opponent_4_strengh_attack.unique().tolist())
```

```python
data[6*len(data)//7:]
```

```python

```
