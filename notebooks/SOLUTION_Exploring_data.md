---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.6.0
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import pandas as pd
```

```python
# Global variables
RAW_DATA = "../data/raw/2020-fpl-data"
TRANSFORMED_DATA_2020 = "../data/transformed/2020_transformed.csv"
DATA_2020_MASTER = pd.read_csv(RAW_DATA_2020)
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
df_elements[(df_elements["web_name"] == "Salah") & (df_elements["gameweek"] == 38)]["event_points"]
```

```python
df_points = df_elements.groupby(["player_id", "gameweek"], as_index=False)["event_points"].last()
df_points = df_points.pivot(index='player_id', columns='gameweek', values='event_points')
point_lookup = df.T.to_dict('list')

df = df_elements[df_elements["gameweek"] != 38]
df["points_next_gw"] =  df.apply(lambda x: point_lookup[x["player_id"]][x["gameweek"]+1], axis=1)
```

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_theme(style="white")


# Compute the correlation matrix
corr = df.corr()

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

```

```python

```
