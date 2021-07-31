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
from fpl.data.io import list_data_dir, load_json
from tqdm import tqdm
import shutil
from pathlib import Path
import os
```

```python
# Defining data folders to sort

DATA_DIR_2020 = "../data/raw/2020-fpl-data/"
DATA_DIR_2021 = "../data/raw/2021-fpl-data/"
```

# Removing unesseary data
Crawlers have not been swithced right after FPL-season ending. We remove redundant data dumps. And if new season is started moving data dumps to 2021-season folder

```python
# Sorting through data dumps gathered upon changing crawler to 2021/2022 season

delete_paths = []
new_season = []
new_season_flag = False

for i, path in enumerate(tqdm(list_data_dir(DATA_DIR_2020))):
    if load_json(path)["events"][-1]["finished"] is True:
        delete_paths.append(path)
        new_season_flag = True
    elif new_season_flag:
        new_season.append(path)


```

```python
# Moving data dumps for new season into DATA_DIR_2021

for i in tqdm(new_season):
    shutil.move(i, Path(DATA_DIR_2021, Path(i).name))
len(list_data_dir(DATA_DIR_2020))
```

```python
# Deleting duplicate data from DATA_DIR_2021 keeping at least 48 after season is finished
for i in tqdm(delete_paths[8:]):
    os.remove(i)
```

```python
# Some numbers of records after sorting

data_20 = list_data_dir(DATA_DIR_2020)
data_21 = list_data_dir(DATA_DIR_2021)


to_data = data_20[-1].name.split("_")[0]
starting_date = data_21[0].name.split("_")[0]

print(f"Number of records 2020/21 season {len(data_20)} to date {to_data}")
print(f"Number of records 2021/22 season {len(data_21)} starting from date {starting_date}")
```

# Creating CSV
We save the sorted data directories as CSV files for later use.

```python
from fpl.data.transformations import to_csv
```

```python
DF_2020 = to_csv(DATA_DIR_2020)
DF_2021 = to_csv(DATA_DIR_2021)
DF_2020.to_csv("../data/transformed/2020_transformed.csv", index=False)
DF_2021.to_csv("../data/transformed/2021_transformed.csv", index=False)
```
