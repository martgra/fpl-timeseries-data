import json
import os
from abc import ABC, abstractmethod
from itertools import chain

from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from fpl.data import io, transformations
from tqdm import tqdm


class CosmoContainer(ABC):
    def __init__(self, endpoint, auth_key, database="Database", container="Container", partition_key=PartitionKey("Key")):
        self.db_account_client = CosmosClient(
            url=endpoint, credential=auth_key)
        self.db = self.db_account_client.create_database_if_not_exists(
            database)
        self.container = self.db.create_container_if_not_exists(container, partition_key=partition_key,
                                                                offer_throughput=400)

    @ abstractmethod
    def _transform_data(self, dict_list):
        return dict_list

    def _get_data(self, data_dir_path):
        data_files = io.list_data_dir(data_dir_path)
        dict_list = []
        for i in data_files:
            dict_list.append(io.load_json(i))
        return dict_list

    def insert_documents(self, data_dir_path, latest=True):
        dict_list = self._get_data(data_dir_path)
        transformed_data_list = self._transform_data(dict_list)

        if latest == True:
            latest_index = self._get_last_insert()
            transformed_data_list = transformed_data_list[self._get_index(
                transformed_data_list, latest_index) + 1:]

        for item in tqdm(transformed_data_list, desc="Migrating to Cosmos"):
            try:
                self.container.create_item(body=item)
            except Exception as e:
                tqdm.write("Could not insert {} from {}, duplicate".format(
                    item["web_name"], item["download_time"]))

    def test_transform(self, data_dir_path):
        dict_list = self._get_data(data_dir_path)
        return self._transform_data(dict_list)[:1]

    def _get_last_insert(self):
        query = "SELECT TOP 1 * FROM c ORDER BY c._ts DESC"
        return list(self.container.query_items(
            query=query, enable_cross_partition_query=True))[0]["id"]

    def _get_index(self, list, latest_id):
        return next((index for (index, d) in enumerate(list) if d["id"] == latest_id), None)

    def search_db(self, query="SELECT * from c"):
        return list(self.container.query_items(
            query=query, enable_cross_partition_query=True))


class ElementsInserter(CosmoContainer):
    def _transform_data(self, dict_list):

        for i in dict_list:
            gameweek = transformations.get_game_week(i["events"])
            download_time = i["download_time"]
            transformations.add_gw_and_download_time(
                i["elements"], download_time, gameweek)
            transformations.add_unique_id(i["elements"])
        return list(chain.from_iterable([i["elements"] for i in dict_list]))


if __name__ == "__main__":
    load_dotenv()
    test_client = ElementsInserter(
        os.getenv("AZURE_COSMOS_URI"), os.getenv("AZURE_COSMOS_TOKEN"), "fplstats", "elements", "download_time")
    # test_client.insert_documents("/home/jason/dev/fpl2021/data")
    print(json.dumps(test_client.search_db(
        "SELECT * from c where c.web_name = 'Willian'"), indent=4))
