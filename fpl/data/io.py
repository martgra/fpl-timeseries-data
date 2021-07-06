"""IO module."""
import json
import os
from pathlib import Path

import pandas as pd


def load_json(file_path: str) -> dict:
    """Load json file.

    Args:
        file_path (str): path to file in format .json

    Returns:
        dict: decoded json
    """
    with open(Path(file_path)) as json_file:
        try:
            return json.load(json_file)
        except json.decoder.JSONDecodeError as error:
            print("Unable to decode JSON. {}".format(error))


def dump_json(file_path: str, data: dict):
    """Dump dict to .json file.

    Args:
        file_path (str): filepath to write
        data (dict): data to write
    """
    with open(Path(file_path), "w", encoding="utf8") as download_file:
        json.dump(data, download_file, ensure_ascii=False, indent=4)


def load_dataframe_from_json(file_path: str, object_to_grab: str) -> object:
    """Load JSON into dataframe.

    Args:
        file_path (str): Path to .json file
        object_to_grab (stri): Key to object to grab

    Returns:
        pandas.DataFrame: dataframe holding json-object
    """
    json_object = load_json(file_path)
    try:
        return pd.DataFrame(json_object[str(object_to_grab)])
    except KeyError as error:
        print("Unable to load dataframe. No key: {}".format(error))


def list_data_dir(dir_path: str, suffix=".json") -> list:
    """List content of a data directory.

    Args:
        dir_path (str): Path to directory to list
        suffix (str, optional): Filter content based on file suffix. Defaults to ".json".

    Returns:
        list: List holding names of files in directory
    """
    return sorted([Path(dir_path, i) for i in os.listdir(dir_path) if Path(i).suffix == suffix])


def get_description_dict(dataframe: pd.DataFrame) -> dict:
    """Return dict with data descripton fields based on dataframe columns.

    Args:
        dataframe (pandas.DataFrame): Dataframe to generate data description schema for

    Returns:
        dict: Dict holding data description based on df columns
    """
    return {
        i: {
            "change": None,
            "description": None,
            "notes": {"personal_notes": None, "official_explanation": None, "referance": None},
            "data_type": None,
            "type": y.name,
            "calculated": None,
        }
        for i, y in zip(dataframe.columns, dataframe.dtypes)
    }


def fix_encoding(data_dir_path: str):
    """Fix files saved in ASCII, overwrites to UTF-8.

    Args:
        data_dir_path (str): Path to directory to fix ascii to utf-8
    """
    for i in list_data_dir(data_dir_path):
        with open(Path(i), "rb") as file:
            json_file = json.load(file)

        with open(Path(i), "w") as file:
            json.dump(json_file, file, ensure_ascii=False, indent=4)
