import json
from pathlib import Path

from fpl.data.io import list_data_dir

for i in list_data_dir("/home/jason/dev/fpl2021/data"):
    with open(Path(i), "rb") as f:
        json_file = json.load(f)

    with open(Path(i), "w") as f:
        json.dump(json_file, f, ensure_ascii=False, indent=4)
