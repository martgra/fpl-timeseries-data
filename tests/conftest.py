"""TODO: add reusable components here"""
from py import test
import pytest
import json
from pathlib import Path

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
        with open(Path(tmp_path,"2020-01-01T0{}-00-00Z_data.json".format(str(i))), "w") as f:
            json.dump(data_object, f)
    print(tmp_path)
    return tmp_path


@pytest.fixture
def data_object():
    with open(Path("tests/2020-01-01T01-00-00Z_test_data.json")) as test_data:
        test_data =json.load(test_data)
    return test_data

