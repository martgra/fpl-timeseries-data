---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import pandas as pd

DATA_2020 = "../data/transformed/transformed_2020.csv"
DATA_2021 = "../data/transformed/transformed_2021.csv"
```

```python
data_2020_df = pd.read_csv(DATA_2020, index_col=0)
```

```python
data_2021_df = pd.read_csv(DATA_2021, index_col=0)
```

```python
import json
with open("../data/raw/2021-fpl-data/2021-08-04T06-00-00Z_data.json") as file:
    teams_df = pd.DataFrame(json.load(file)["teams"])
```

```python
data_2020_df = data_2020_df[data_2020_df["download_time"] != data_2020_df["download_time"].tolist()[0]]
data_2020_grouped = data_2020_df.groupby(["code", "gameweek"], as_index=False)[["event_points", "web_name", "element_type", "minutes", "team"]].last()
```

```python
with open("../data/2021_fixtures/fixtures_2021.json") as file:
    fixtures = json.load(file)["fixtures"]
    
with open("../data/raw/2021-fpl-data/2021-08-04T06-00-00Z_data.json") as file:
    teams = json.load(file)["teams"]

teams = {i["id"]: i["name"] for i in teams}

all_teams = {}
for team in teams:
    opponents = []
    for fixture in fixtures:
        if fixture["team_h"] == team:
            opponents.append(
                    {
                        "team": teams[fixture["team_a"]],
                        "difficulty": fixture["team_h_difficulty"],
                        "venue": "h",
                        "gameweek": fixture["event"],
                    }
                )
        if fixture["team_a"] == team:
            opponents.append(
                    {
                        "team": teams[fixture["team_h"]],
                        "difficulty": fixture["team_a_difficulty"],
                        "venue": "a",
                        "gameweek": fixture["event"],
                    }
                )
    all_teams[teams[team]] = opponents

from statistics import mean, pstdev
difficulty_planner = {}

num_matches = 5

for team in teams:
    difficulty_planner[teams[team]] = [round(mean([i["difficulty"] for i in all_teams[teams[team]][:num_matches]]),2), pstdev([i["difficulty"] for i in all_teams[teams[team]][:num_matches]])]
team_difficulty_df = pd.DataFrame([{"name": i, "mean_diff":y[0], "std_diff": y[1]} for i, y in difficulty_planner.items()])
```

```python
def sort_players(old_df, new_df, new_teams, new_teams_difficulty, pos=1):   
    old_df = old_df[old_df["download_time"] != data_2020_df["download_time"].tolist()[0]]
    old_df = old_df.groupby(["code", "gameweek"], as_index=False)[["event_points", "web_name", "element_type", "minutes", "team"]].last()
    new_df = new_df.groupby("code", as_index=False)[["now_cost", "team", "element_type"]].last()
    new_df = new_df.set_index("code")
    old_df  = old_df.join(new_df[["element_type"]], on="code", rsuffix="_new") 
    old_df = old_df.loc[old_df["element_type_new"] == pos]
    
    for id in old_df["code"].unique():
        old_df.loc[old_df["code"] == id, "minutes"] = old_df.loc[old_df["code"] == id][["minutes"]].diff().fillna(old_df.loc[old_df["code"] == id]["minutes"])
        
    old_df = old_df.groupby("code").agg({"minutes": "mean", "event_points": "mean", "web_name": "last"}).sort_values(by=["event_points"], ascending=False)
    old_df = old_df.join(new_df, on='code').sort_values(by=["event_points", "now_cost"], ascending=[False, True])
    old_df = old_df.join(new_teams[["id", "name", "strength_attack_home", "strength_attack_away", "strength_defence_home", "strength_defence_away"]].set_index('id'), on="team")
    old_df = old_df.join(new_teams_difficulty.set_index("name"), on="name")
    old_df.dropna(inplace=True)
    old_df["event_points"] = old_df["event_points"].round(1)
    old_df["minutes"] = old_df["minutes"].round(0)    
    return old_df
```

```python
def filter_players(df, minutes=50, price_lower=0.0, price_upper=13, attack=True, num=1, team=True):
    sorted_df = df[(df["minutes"] > minutes) & (df["now_cost"] <= price_upper*10) & (df["now_cost"] >= price_lower*10)].sort_values(by=["event_points",  "minutes"], ascending=[False, False])
    
    if attack:
        strength_home = "strength_attack_home"
        strength_away = "strength_attack_away"
    else:
        strength_home = "strength_defence_home"
        strength_away = "strength_defence_away"
        
    sorted_df = sorted_df.sort_values(by=["mean_diff", strength_home, strength_away], ascending=[True, False, False])
    if team:
        return sorted_df.groupby("name").first().sort_values(by=["mean_diff", "event_points"], ascending=[True,False]).iloc[:num]
    else: 
        return sorted_df.sort_values(by=["mean_diff", "event_points"], ascending=[True,False]).iloc[:num]
```

```python
old_df = sort_players(data_2020_df, data_2021_df, teams_df, team_difficulty_df, pos=1)
old_df
filter_players(old_df, minutes=50, price_upper=13, num=10, team=True)
```

```python

```

```python

```
