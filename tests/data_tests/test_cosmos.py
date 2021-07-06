from sys import dont_write_bytecode

from azure.cosmos import ContainerProxy, CosmosClient, DatabaseProxy

from fpl.data.cosmos import ElementsInserter
from fpl.data.io import dump_json, list_data_dir, load_json
from fpl.data.transformations import add_gw_and_download_time, add_unique_id


def test_ElementsInserter(cosmos_client, small_data_dir):
    assert isinstance(cosmos_client, ElementsInserter)
    assert isinstance(cosmos_client.cosmos_account_client, CosmosClient)
    assert isinstance(cosmos_client.database, DatabaseProxy)
    assert isinstance(cosmos_client.container, ContainerProxy)
    cosmos_client.insert_documents(small_data_dir)
    assert len(cosmos_client.search_db()) == 2


def test_migrate_db(cosmos_client, small_data_dir, data_object, capsys):
    cosmos_client.insert_documents(small_data_dir, latest=False)
    cosmos_client.insert_documents(small_data_dir, latest=True)
    capture = capsys.readouterr()
    assert "Local data and Cosmos DB in sync" in capture.out

    # Removing the 5th element from cosmos
    add_gw_and_download_time(data_object["elements"], data_object["download_time"], 1)
    add_unique_id(data_object["elements"])
    cosmos_client.delete_items([data_object["elements"][1]])
    cosmos_client.insert_documents(small_data_dir)
    capture = capsys.readouterr()
    assert "Migrating from index 0:1" in capture.out

    files = list_data_dir(small_data_dir)
    loaded_json = load_json(files[0])
    loaded_json["elements"] = loaded_json["elements"][:-1]
    dump_json(files[0], loaded_json)
    cosmos_client.insert_documents(small_data_dir)
    capture = capsys.readouterr()
    assert "Cosmos DB ahead of local data." in capture.out

    cosmos_client.insert_documents(small_data_dir, latest=False)
    capture = capsys.readouterr()
    assert "Could not insert" in capture.out


def test_game_weeks(cosmos_client, small_data_dir):
    assert not cosmos_client.get_latest_download()
    cosmos_client.insert_documents(small_data_dir)
    print(cosmos_client.search_db())
    print(cosmos_client.get_latest_download())
