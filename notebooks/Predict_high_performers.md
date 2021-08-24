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
import json 
from fpl.data.io import list_data_dir, load_json
from fpl.data.transformations import add_gw_and_download_time, add_unique_id, get_game_week, to_csv
from tqdm import tqdm
```

# Syr sammen datakilder

```python
elements_2020_df = pd.read_csv("../data/transformed/transformed_2020.csv", index_col=0)
fixtures_2020 = list_data_dir("../data/raw/2020_fixtures/") 
team_data_2020 = "../data/raw/2020-fpl-data/"
```

```python
teams_df = to_csv("teams", team_data_2020, fixtures_path="../data/raw/2020_fixtures/")
```

```python
teams = {i: y for i,y in zip(teams_df["id"].unique().tolist(),teams_df["name"].unique().tolist())}
```

```python
gameweek_fixtures = []
for path in fixtures_2020:
    with open(path) as file:
        fixtures = json.load(file)["fixtures"]
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
    gameweek_fixtures.append(all_teams)
```

```python
teams_df_g = teams_df.loc[teams_df["gameweek"] < 38].groupby(["name", "gameweek"], as_index=False).last()
teams_df_g.columns
```

```python
def add_opponents(row):
    opponents_row = {"name": row["name"], "gameweek":row["gameweek"]}
    opponents_row["gameweek"] = row["gameweek"]
    teams = gameweek_fixtures[row["gameweek"]-1][row["name"]][row["gameweek"]:row["gameweek"]+5]
    opponents_row.update({f"{key}_{i}": teams[i][key] for i,y in enumerate(teams) for key in ["team", "difficulty", "venue"]})
    return opponents_row

temp = [{'team': 'Fulham',
    'difficulty': 2,
    'venue': 'a',
    'gameweek': 1.0},
   {'team': 'West Ham', 'difficulty': 2, 'venue': 'h', 'gameweek': 2.0},
   {'team': 'Liverpool', 'difficulty': 5, 'venue': 'a', 'gameweek': 3.0}]

```

```python
opponents = teams_df_g.apply(lambda x:  add_opponents(x), axis=1, result_type="expand")
```

```python
def add_strength(row, teams_df):
    if row.iloc[1] == "a":
        return {"strength": int(teams_df[(teams_df["name"] == row.iloc[0]) &  (teams_df["gameweek"] == row.iloc[2])]["strength_overall_home"])} 
    elif row.iloc[1] == "h":
        return {"strength": int(teams_df[(teams_df["name"] == row.iloc[0]) &  (teams_df["gameweek"] == row.iloc[2])]["strength_overall_away"])} 


for i in range(5):
    opponents[f"opponent_strength_{i}"] = opponents.apply(lambda x: add_strength(x[[f"team_{i}", f"venue_{i}", "gameweek"]], teams_df_g), axis=1, result_type="expand")
```

```python
opponents = opponents[sorted(opponents.columns, key=lambda x: x.split("_")[-1] if "_" in x else "-1")]
```

```python
teams_df_g = teams_df_g.join(opponents.set_index(["name", "gameweek"]), on=["name", "gameweek"])
```

```python
elements_2020_df = elements_2020_df.join(teams_df_g.set_index(["id", "gameweek"]), on=["team", "gameweek"], rsuffix="_team")

```

```python
columns = elements_2020_df.columns.tolist()
columns.insert(0, columns.pop(columns.index("name")))
columns.insert(0, columns.pop(columns.index("web_name")))
elements_2020_df = elements_2020_df[columns]
```

```python
elements_2020_df_g = elements_2020_df.groupby(["code", "gameweek"], as_index=False).last()
```

```python
def calculate_target(row):
    return elements_2020_df_g[(elements_2020_df_g["code"] == row["code"]) & (elements_2020_df_g["gameweek"] > row["gameweek"]) & (elements_2020_df_g["gameweek"] <= row["gameweek"]+5)]["event_points"].mean()
```

```python
elements_2020_df_g["target"] = elements_2020_df_g.apply(calculate_target, axis=1, result_type="expand")
```

# Vasker data

```python
drop_text = [i for i,y in elements_2020_df_g.dtypes.to_dict().items() if ((y == "O" or "text" in i) and "venue" not in i)]
```

```python
na_filled = elements_2020_df_g.drop(drop_text, axis=1).interpolate(method='linear', limit_direction='backward', axis=0)
na_filled = na_filled.interpolate(method='linear', limit_direction='forward', axis=0)
```

```python
for code in na_filled.code.unique().tolist():
    for column in ["bonus", "bps", "ict_index", "clean_sheets", "creativity", "goals_conceded", "goals_scored", "influence", "minutes",
                   "own_goals", "penalties_saved", "red_cards", "saves", "threat", "yellow_cards"]:
        try:
            index = na_filled.loc[na_filled.code == code, column]
            index.iloc[0] = index.iloc[1] 
            index.iloc[1:] = index.iloc[1:].diff().fillna(index.iloc[1:]).rolling(5, min_periods=1).mean()
            na_filled.loc[na_filled.code == code, column] = index
        except Exception as e:
            pass
```

```python
cat_columns = na_filled.select_dtypes(['O']).columns
na_filled[cat_columns] = na_filled[cat_columns].astype('category')
cat_columns = na_filled.select_dtypes(['category']).columns
na_filled[cat_columns] = na_filled[cat_columns].apply(lambda x: x.cat.codes)
```

```python
na_filled = na_filled.drop(["total_points","squad_number", "code", "gameweek", "pulse_id", "code_team" ,"player_id", "draw", "position", "win", "loss", "played", "points", "special", "value_season", ], axis=1)
```

```python
 na_filled = na_filled.drop(['cost_change_start',
 'cost_change_start_fall',
 'event_points',
 'in_dreamteam',
 'selected_by_percent',
 'team',
 'team_code',
 'transfers_in',
 'transfers_out',
 'own_goals',
 'penalties_missed',
 'red_cards',
 'bonus',
 'influence_rank',
 'creativity_rank',
 'threat_rank',
 'ict_index_rank',
 'corners_and_indirect_freekicks_order',
 'direct_freekicks_order',
 'strength_overall_home',
 'strength_overall_away',
 'venue_0',
 'venue_1',
 'venue_2',
 'venue_3',
 'venue_4'], axis=1)
```

```python
na_filled_backup = na_filled
#na_filled = na_filled.loc[na_filled.target != 0]
na_filled_backup
```

```python
from sklearn.metrics import r2_score

r2_score(na_filled.target, na_filled.points_per_game)
```

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(na_filled.iloc[:,:-1], na_filled.iloc[:,-1], test_size=0.33, random_state=42)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)
```

```python
na_filled.target.value_counts(0)
```

```python
from sklearn.linear_model import LinearRegression
reg = LinearRegression().fit(X_train, y_train)
reg.score(X_test, y_test)
```

```python
from sklearn.ensemble import RandomForestRegressor
regr = RandomForestRegressor(max_depth=25, n_estimators=200, random_state=0)
regr.fit(X_train, y_train)
regr.score(X_test, y_test)
```

```python
from sklearn.model_selection import RandomizedSearchCV
import numpy as np

#Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 50, stop = 300, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 55, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

# Use the random grid to search for best hyperparameters
# First create the base model to tune
rf = RandomForestRegressor()
# Random search of parameters, using 3 fold cross validation, 
# search across 100 different combinations, and use all available cores
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 10, cv = 3, verbose=2, random_state=42, n_jobs = -1)
# Fit the random search model
rf_random.fit(X_train, y_train)
```

```python
best_random = rf_random.best_estimator_
best_random.score(X_test, y_test)
```

```python
score_x = best_random.predict(X_test)
```

```python
r2_score(y_test, score_x)
```

```python
importance = pd.DataFrame([best_random.feature_importances_]) 
importance.columns=na_filled.columns.tolist()[:-1]

```

```python

importance.idxmax(axis=1)
```

```python
pd.set_option("display.max_columns", None)
importance.sort_values(by=[0], axis=1, ascending=False)
```

# Predict 2021 players

```python
import pandas as pd
elements_2021_df = pd.read_csv("../data/transformed/transformed_2021.csv", index_col=0)
```

```python
elements_2021_df = elements_2021_df.groupby("code", as_index=False).last()
```

```python
last_5 = pd.read_csv("../data/transformed/transformed_2020.csv", index_col=0)
```

```python
last_5 = last_5.groupby(["code", "gameweek"], as_index=False).last()
last_5 = last_5.loc[last_5["gameweek"] > 38-5]
```

```python
for code in last_5.code.unique().tolist():
    for column in ["bonus", "bps", "ict_index", "clean_sheets", "creativity", "goals_conceded", "goals_scored", "influence", "minutes",
                   "own_goals", "penalties_saved", "red_cards", "saves", "threat", "yellow_cards"]:
        try:
            index = last_5.loc[last_5.code == code, column]
            index = index.diff().fillna(index)
            last_5.loc[last_5.code == code, column] = index
        except Exception as e:
            pass
```

```python
last_5 = last_5.loc[last_5["gameweek"] > 38-4]
last_5.loc[last_5.minutes > 90, "minutes"] = last_5.loc[last_5.minutes > 90, "minutes"]/2
last_5["gameweek"] = last_5["gameweek"] - 38 
last_5 = last_5.append(elements_2021_df)
last_5 = last_5.sort_values(by=["code", "gameweek"], ignore_index=True)
last_5 = last_5.loc[last_5.code.isin(elements_2021_df.code.unique())]

```

```python
for code in last_5.code.unique().tolist():
    for column in ["bonus", "bps", "ict_index", "clean_sheets", "creativity", "goals_conceded", "goals_scored", "influence", "minutes",
                   "own_goals", "penalties_saved", "red_cards", "saves", "threat", "yellow_cards"]:
        try:
            index = last_5.loc[last_5.code == code, column]

            last_5.loc[last_5.code == code, column] = index.mean()
        except Exception as e:
            pass
```

```python
last = last_5.groupby("code").last()
```

```python
merged_g = last
```

```python
teams_21_df = to_csv("teams", "../data/raw/2021-fpl-data/")
```

```python
teams_21_df_g = teams_21_df.loc[teams_21_df["gameweek"] < 38].groupby(["name"], as_index=False).last()
```

```python
teams = {i: y for i,y in zip(teams_21_df_g["id"].unique().tolist(),teams_21_df_g["name"].unique().tolist())}
fixtures_2021 = list_data_dir("../data/2021_fixtures/") 
```

```python
gameweek_fixtures = []
for path in fixtures_2021[-1:]:
    with open(path) as file:
        fixtures = json.load(file)["fixtures"]
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
    gameweek_fixtures.append(all_teams)
```

```python
opponents = teams_21_df_g.apply(lambda x:  add_opponents(x), axis=1, result_type="expand")
```

```python
for i in range(5):
    opponents[f"opponent_strength_{i}"] = opponents.apply(lambda x: add_strength(x[[f"team_{i}", f"venue_{i}", "gameweek"]], teams_21_df_g), axis=1, result_type="expand")
opponents = opponents[sorted(opponents.columns, key=lambda x: x.split("_")[-1] if "_" in x else "-1")]
```

```python
teams_21_df_g = teams_21_df_g.join(opponents.set_index(["name", "gameweek"]), on=["name", "gameweek"])
```

```python
elements_2021_df_merged = merged_g.join(teams_21_df_g.set_index(["id", "gameweek"]), on=["team", "gameweek"], rsuffix="_team")
```

```python
pd.set_option("display.max_columns", None)
elements_2021_df_merged
```

```python
drop_text = [i for i,y in elements_2021_df.dtypes.to_dict().items() if ((y == "O" or "text" in i) and "venue" not in i)]
codes = elements_2021_df_merged["code"]
elements_2021_df_merged = elements_2021_df_merged.drop(drop_text, axis=1)
elements_2021_df_merged =elements_2021_df_merged.drop([i for i in elements_2021_df_merged.columns.tolist() if not i in na_filled_backup.columns.tolist()], axis=1)
```

```python
cat_columns = elements_2021_df_merged.select_dtypes(['O']).columns
elements_2021_df_merged[cat_columns] = elements_2021_df_merged[cat_columns].astype('category')
cat_columns = elements_2021_df_merged.select_dtypes(['category']).columns
elements_2021_df_merged[cat_columns] = elements_2021_df_merged[cat_columns].apply(lambda x: x.cat.codes)
```

```python
elements_2021_df_merged["chance_of_playing_next_round"] = elements_2021_df_merged["chance_of_playing_next_round"].fillna(100)
elements_2021_df_merged["chance_of_playing_this_round"] = elements_2021_df_merged["chance_of_playing_this_round"].fillna(100)
```

```python
elements_2021_df_merged.interpolate(method='linear', limit_direction='forward', axis=0)
elements_2021_df_merged = elements_2021_df_merged.fillna(100)

```

```python
elements_2021_df_merged.columns.tolist()
```

```python
elements_2021_df_merged_scaled = scaler.transform(elements_2021_df_merged)
```

```python
results = pd.DataFrame()
results["pred"] = codes
```

```python
results["pred"] = best_random.predict(elements_2021_df_merged_scaled)
```

```python
elements_2021_df = pd.read_csv("../data/transformed/transformed.csv", index_col=0)
elements_2021_df = elements_2021_df.groupby(["code"]).last()
results_selected = results.join(elements_2021_df, on=["code"])[["web_name", "pred", "now_cost", "element_type"]]
```

```python
results_selected[(results_selected.element_type == 3) & (results_selected.now_cost <= 130) & (results_selected.now_cost >= 40)].sort_values(by=["pred", "now_cost"], ascending=[False, True]).iloc[:40]
```

```python
results_selected[results_selected.web_name == "Mount"]
```

```python
for i in elements_2021_df_merged.describe():
    print(i)
    print(elements_2021_df_merged.describe()[i].iloc[1:].loc[["mean", "std", "min", "max"]].to_dict())
    print(na_filled_backup.describe()[i].iloc[1:].loc[["mean", "std", "min", "max"]].to_dict())
    input("Press Enter to continue...")
```

```python

```
