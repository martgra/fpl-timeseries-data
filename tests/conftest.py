"""TODO: add reusable components here"""
import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from fpl.data.cosmos import ElementsInserter
from fpl.data.transformations import add_gw_and_download_time, add_unique_id


@pytest.fixture
def data_dir(tmp_path, data_object):
    """Return a path to a directory loaded with 12 mock files

    Args:
        tmp_path (pathlib.Path): Path to temporary directory created by generic pytest fixture tmp_path

    Returns:
        pathlib.Path: Path to temporary directory holding 4 mock files, simulating the data folder
    """
    with open(Path(tmp_path, str(".gitkeep")), "w") as f:
        f.write("test1")
    with open(Path(tmp_path, str("test.xlsx")), "w") as f:
        f.write("test2")
    for i in range(2):
        with open(Path(tmp_path, "2020-01-01T0{}-00-00Z_data.json".format(str(i))), "w") as f:
            json.dump(data_object, f)
    return tmp_path


@pytest.fixture
def small_data_dir(tmp_path, data_object):
    data_object["elements"] = data_object["elements"][0:2]
    with open(Path(tmp_path, "2020-01-01T01-00-00Z_data.json"), "w") as f:
        json.dump(data_object, f)
    return tmp_path


@pytest.fixture
def data_object():
    with open(Path("tests/2020-01-01T01-00-00Z_test_data.json")) as test_data:
        test_data = json.load(test_data)
    return test_data


def transformed_data_object(data_object):
    add_gw_and_download_time(data_object["elements"], data_object["download_time"], 1)
    add_unique_id(data_object["elements"])
    return data_object


@pytest.fixture
def fixtures_object():
    with open(Path("tests/data_tests/fixtures_mock.json")) as test_data:
        test_data = json.load(test_data)
    return test_data


@pytest.fixture
def teams_fixtures(requests_mock, fixtures_object):
    requests_mock.get("https://fantasy.premierleague.com/api/mock/", json=fixtures_object)


@pytest.fixture
def cosmos_client():
    load_dotenv()
    cosmos_client = ElementsInserter(
        os.getenv("AZURE_COSMOS_URI"),
        os.getenv(
            "AZURE_COSMOS_TOKEN",
        ),
        database_meta={
            "database": "fplstats",
            "container": "test_elements",
            "partition_key": "id",
        },
    )
    yield cosmos_client
    clean = cosmos_client.search_db(query="SELECT c.id from c")
    cosmos_client.delete_items(clean)
