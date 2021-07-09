---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import pandas as pd
```

```python
# Global variables
RAW_DATA_2020 = "../data/transformed/2020_transformed.csv"
DATA_2020_MASTER = pd.read_csv(RAW_DATA_2020)
```

```python
df_elements = DATA_2020_MASTER.fillna(-99)
```

```python
df_changes_total = df_elements.groupby(["player_id"]).nunique()
changes_total = {x: {"mean": y, "count": z} for x,y ,z in list(zip(df_changes_total.columns, df_changes_total.mean().tolist(), df_changes_total.mode().iloc[0].tolist()))}
```

```python
df_changes_gw = df_elements.groupby(["player_id", "gameweek"]).nunique()
changes_gw = {x: {"mean_gw": y, "count_gw": z} for x,y ,z in list(zip(df_changes_gw.columns, df_changes_gw.mean().tolist(), df_changes_gw.mode().iloc[0].tolist()))}
```

```python
df = df_elements[df_elements["gameweek"] != 38]
df_changes_gw = df.groupby(["gameweek", "player_id"]).nunique()
changes_gw_filtered = {x: {"mean_gw_filtered": y, "count_gw_filtered": z} for x,y ,z in list(zip(df_changes_gw.columns, df_changes_gw.mean().tolist(), df_changes_gw.mode().iloc[0].tolist()))}
```

```python
df = pd.DataFrame(changes_total)
df = df.append(pd.DataFrame(changes_gw))
df = df.append(pd.DataFrame(changes_gw_filtered))

```

```python
drop_columns = [i for i in df.columns if df.loc["mean"][i] == df.loc["count"][i] == 1 or df.loc["count"][i] == 1015]
```

```python
df_elements = df_elements.drop(columns=["code"])
```

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_theme(style="white")


# Compute the correlation matrix
corr = df_elements.corr()

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(30, 20))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.2, cbar_kws={"shrink": .5})







```

```python
df_elements[(df_elements["web_name"] == "Salah") & (df_elements["gameweek"] == 38)]["event_points"]
```

```python
df_points = df_elements.groupby(["player_id", "gameweek"], as_index=False)["event_points"].last()

```

```python
df = df_points.pivot(index='player_id', columns='gameweek', values='event_points')
df
```

```python
point_lookup = df.T.to_dict('list')

```

```python
df = df_elements[df_elements["gameweek"] != 38]
df["points_next_gw"] =  df.apply(lambda x: point_lookup[x["player_id"]][x["gameweek"]+1], axis=1)
```

```python
!pip install scikit-learn
```

```python
train = df.iloc[:int(len(df)*0.9)]
test =  df.iloc[int(len(df)*0.9):]

X = train [[
    "chance_of_playing_next_round",
    "chance_of_playing_this_round",
    "cost_change_event",
    "cost_change_event_fall",
    "cost_change_start",
    "cost_change_start_fall",
    "dreamteam_count",
    "element_type",
    "ep_next",
    "ep_this",
    "event_points",
    "form",
    "in_dreamteam",
    "now_cost",
    "points_per_game",
    "selected_by_percent",
    "team_code",
    "total_points",
    "transfers_in",
    "transfers_in_event",
    "transfers_out",
    "transfers_out_event",
    "value_form",
    "value_season",
    "minutes",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "own_goals",
    "penalties_saved",
    "penalties_missed",
    "yellow_cards",
    "red_cards",
    "saves",
    "bonus",
    "bps",
    "influence",
    "creativity",
    "threat",
    "ict_index",
    "influence_rank",
    "influence_rank_type",
    "creativity_rank",
    "creativity_rank_type",
    "threat_rank",
    "threat_rank_type",
    "ict_index_rank",
    "ict_index_rank_type",
    "corners_and_indirect_freekicks_order",
    "direct_freekicks_order",
    "penalties_order",
]]
y = train["points_next_gw"]
```

```python
X.info()
```

```python
from sklearn.linear_model import LinearRegression
reg = LinearRegression().fit(X, y)
```

```python
X_test = test [[
    "chance_of_playing_next_round",
    "chance_of_playing_this_round",
    "cost_change_event",
    "cost_change_event_fall",
    "cost_change_start",
    "cost_change_start_fall",
    "dreamteam_count",
    "element_type",
    "ep_next",
    "ep_this",
    "event_points",
    "form",
    "in_dreamteam",
    "now_cost",
    "points_per_game",
    "selected_by_percent",
    "team_code",
    "total_points",
    "transfers_in",
    "transfers_in_event",
    "transfers_out",
    "transfers_out_event",
    "value_form",
    "value_season",
    "minutes",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "own_goals",
    "penalties_saved",
    "penalties_missed",
    "yellow_cards",
    "red_cards",
    "saves",
    "bonus",
    "bps",
    "influence",
    "creativity",
    "threat",
    "ict_index",
    "influence_rank",
    "influence_rank_type",
    "creativity_rank",
    "creativity_rank_type",
    "threat_rank",
    "threat_rank_type",
    "ict_index_rank",
    "ict_index_rank_type",
    "corners_and_indirect_freekicks_order",
    "direct_freekicks_order",
    "penalties_order",
]]

y_test = test[["points_next_gw"]]
```

```python
reg.score(X_test, y_test)
```

```python

```

```python
for i in range(100,150):
    print(f"name: {test.iloc[i:i+1]['web_name'].tolist()[0]} predicted: { reg.predict(X_test.iloc[i:i+1])[0]}  actual: {test.iloc[i:i+1]['points_next_gw'].tolist()[0]}")
```

```python
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor

X = df[[
    "chance_of_playing_next_round",
    "chance_of_playing_this_round",
    "cost_change_event",
    "cost_change_event_fall",
    "cost_change_start",
    "cost_change_start_fall",
    "dreamteam_count",
    "element_type",
    "ep_next",
    "ep_this",
    "event_points",
    "form",
    "in_dreamteam",
    "now_cost",
    "points_per_game",
    "selected_by_percent",
    "team_code",
    "total_points",
    "transfers_in",
    "transfers_in_event",
    "transfers_out",
    "transfers_out_event",
    "value_form",
    "value_season",
    "minutes",
    "goals_scored",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "own_goals",
    "penalties_saved",
    "penalties_missed",
    "yellow_cards",
    "red_cards",
    "saves",
    "bonus",
    "bps",
    "influence",
    "creativity",
    "threat",
    "ict_index",
    "influence_rank",
    "influence_rank_type",
    "creativity_rank",
    "creativity_rank_type",
    "threat_rank",
    "threat_rank_type",
    "ict_index_rank",
    "ict_index_rank_type",
    "corners_and_indirect_freekicks_order",
    "direct_freekicks_order",
    "penalties_order",
]]

y = df[["points_next_gw"]]
```

```python
regressor = DecisionTreeRegressor(random_state=0)
cross_val_score(regressor, X, y, cv=10)
```

```python

```
