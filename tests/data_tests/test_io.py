"""Test IO module."""
from pathlib import Path

import pandas as pd

from fpl.data.io import (
    dump_json,
    fix_encoding,
    get_description_dict,
    list_data_dir,
    load_dataframe_from_json,
    load_json,
)
from tests.conftest import data_dir


def test_list_data_dir(data_dir):
    assert len(list_data_dir(data_dir)) == 2
    assert len(list_data_dir(data_dir, suffix=".gitkeep")) == 0
    assert len(list_data_dir(data_dir, suffix=".xlsx")) == 1


def test_get_description_dict():
    descriptions_dict = get_description_dict(
        pd.DataFrame([{"test1": 0.5, "test2": 5, "test3": None}])
    )
    assert isinstance(descriptions_dict, dict)
    assert descriptions_dict["test1"] == {
        "change": None,
        "description": None,
        "notes": {
            "personal_notes": None,
            "official_explanation": None,
            "referance": None,
        },
        "data_type": None,
        "type": "float64",
        "calculated": None,
    }
    assert descriptions_dict["test2"]["type"] == "int64"
    assert descriptions_dict["test3"]["type"] == "object"


def test_load_json(data_dir, data_object, capsys):
    assert (
        load_json(Path(data_dir, "2020-01-01T01-00-00Z_data.json"))["elements"][0]
        == data_object["elements"][0]
    )

    load_json(Path(data_dir, ".gitkeep"))
    capture = capsys.readouterr()
    assert capture.out == "Unable to decode JSON. Expecting value: line 1 column 1 (char 0)\n"


def test_dump_json(data_dir):
    test_json = {"test1": "test"}
    dump_json(Path(data_dir, "test_json.json"), test_json)
    assert load_json(Path(data_dir, "test_json.json")) == test_json


def test_load_dataframe_from_json(data_dir, data_object, capsys):
    json_path = Path(data_dir, "2020-01-01T01-00-00Z_data.json")
    data_frame = load_dataframe_from_json(json_path, "elements")
    assert isinstance(data_frame, pd.DataFrame)
    assert len(data_frame.columns) == len(data_object["elements"][0].keys())

    load_dataframe_from_json(json_path, "skrellements")
    capture = capsys.readouterr()
    assert capture.out == "Unable to load dataframe. No key: 'skrellements'\n"


def test_fix_encodings(data_dir):
    fix_encoding(data_dir)
