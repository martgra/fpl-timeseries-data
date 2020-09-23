import json
import os
from pathlib import Path

import pandas as pd


def load_json(file_path):
    """Load json file

    Args:
        file_path (str): path to file in format .json

    Returns:
        dict: decoded json
    """
    with open(Path(file_path)) as json_file:
        try:
            return json.load(json_file)
        except json.decoder.JSONDecodeError:
            print("Unable to decode json")


def dump_json(file_path):
    pass


def load_dataframe_from_json(file_path, object_to_grab):
    """load JSON into dataframe

    Args:
        file_path (str): Path to .json file
        object_to_grab (stri): Key to object to grab

    Returns:
        pandas.DataFrame: dataframe holding json-object
    """
    json_object = load_json(file_path)
    try:
        return pd.DataFrame(json_object[str(object_to_grab)])
    except Exception:
        print("Could not load dataframe")
    except KeyError:
        print("Key not found")


def list_data_dir(dir_path, suffix=".json"):
    """List content of a data directory

    Args:
        dir_path (str): Path to directory to list
        suffix (str, optional): Filter content based on file suffix. Defaults to ".json".

    Returns:
        list: List holding names of files in directory 
    """
    return sorted([Path(dir_path, i) for i in os.listdir(dir_path) if Path(i).suffix == suffix])


def get_description_dict(dataframe):
    """Returns dict with data descripton fields based on dataframe columns

    Args:
        dataframe (pandas.DataFrame): Dataframe to generate data description schema for

    Returns:
        dict: Dict holding data description based on df columns
    """
    return {i: {
        "change": "None",
        "description": "None",
        "notes": {
            "personal_notes": "None",
            "official_explanation": "None",
            "referance": "None"},
        "data_type": "None",
        "type": "None",
        "calculated": "cumulative_sum"
    } for i in dataframe.columns}
