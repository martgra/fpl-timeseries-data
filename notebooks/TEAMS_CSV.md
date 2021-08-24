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
```

```python
dataframe = pd.read_csv("../fixtures.csv.2")
```

```python
with open("../data/raw/2020-fpl-data/2020-09-12T08-24-34Z_data.json") as file:
    teams = json.load(file)["teams"]
```

```python

```

```python
all_teams = []
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
    all_teams.append({teams[team]: opponents})
```

```python
all_teams
```

```python

```
