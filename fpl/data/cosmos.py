"""Interface to Cosmos DB."""

import os
import sys
from abc import ABC, abstractmethod
from itertools import chain

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError
from dotenv import load_dotenv
from tqdm import tqdm

from fpl.data import io, transformations


class CosmoContainer(ABC):
    """Abstract class for interacting with Cosmos DB collections.

    Class holding holistic methods to interact with Cosmos DB regardless of collection type.
    The abstract method to override will be transformation which will differ
    based on collection specific transformation.
    See https://docs.microsoft.com/en-us/azure/cosmos-db/sql-api-sdk-python for futher reference.

    Attributes:
        cosmos_account_client (azure.cosmos.CosmosClient): Cosmos account client
        database (azure.cosmos.DatabaseProxy): Cosmos Database proxy client
        container (azure.cosmos.ContainerProxy): Cosmos container client

    Example:
        load_dotenv()
        cosmos_element_client = ElementsInserter(
            os.getenv("AZURE_COSMOS_URI"),
            os.getenv("AZURE_COSMOS_TOKEN"),
            {"database": "fplstats", "container": "elements", "partition_key": "download_time"},
        )
        latest_gameweek_data = cosmos_element_client.get_latest_gameweek()[:1]
    """

    def __init__(self, endpoint, auth_key, database_meta):
        """Initialize Cosmos container object.

        Args:
            endpoint (str): The Cosmos Database URI.
            auth_key (str): The Cosmos Database PRIMARY or SECONDARY password
            database_meta (dict of str:str): Holds 'database', 'container' and 'partition_key'
        """
        self.cosmos_account_client = CosmosClient(url=endpoint, credential=auth_key)
        self.database = self.cosmos_account_client.create_database_if_not_exists(
            database_meta["database"]
        )
        self.container = self.database.create_container_if_not_exists(
            database_meta["container"],
            partition_key=PartitionKey(database_meta["partition_key"]),
            offer_throughput=400,
        )

    @abstractmethod
    def _transform_data(self, dict_list: list) -> list:
        """Abstract method for transforming data.

        Args:
            dict_list (list[dict]): list holding dicts to be transformed

        Returns:
            list[dict]: list of transformed dicts
        """
        return dict_list

    @staticmethod
    def _get_data(data_dir_path: str) -> list:
        """Load list of .json files to list of dicts.

        Args:
            data_dir_path (str): Path to directory holding

        Returns:
            list[dict]: list of dicts holding loaded .json
        """
        data_files = io.list_data_dir(data_dir_path)
        dict_list = []
        for i in data_files:
            dict_list.append(io.load_json(i))
        return dict_list

    @staticmethod
    def _get_index(dict_list: list, latest_id: str) -> int:
        """Get index of dict with document["id].

        Args:
            dict_list (list[dict]): list containing dicts to scan for latest insert to Cosmos
            latest_id (str): document["id"] of latest insert found in Cosmos

        Returns:
            int: Index of latest inserted document compared to local data
        """
        if latest_id not in [i["id"] for i in dict_list]:
            print("Cosmos DB ahead of local data")
            return len(dict_list)
        return next((index for (index, d) in enumerate(dict_list) if d["id"] == latest_id), None)

    def insert_documents(self, data_dir_path: str, latest=True):
        """Migrate local documents to Cosmos DB.

        Args:
            data_dir_path (str): Path to directory holding data to migrate
            latest (bool, optional): Indicates if all data are to be migrated,
                or just from latest inserted document. Defaults to True.
        """
        dict_list = self._get_data(data_dir_path)
        transformed_data_list = self._transform_data(dict_list)

        if latest:
            latest_insert = transformed_data_list, self._get_last_insert()
            if latest_insert:
                latest_index = self._get_index(transformed_data_list, self._get_last_insert())
                if latest_index == len(transformed_data_list) - 1:
                    print("Local data and Cosmos DB in sync")
                    sys.exit(0)
                else:
                    print(
                        "Migrating from index{}:{}".format(latest_index, len(transformed_data_list))
                    )
                    transformed_data_list = transformed_data_list[latest_index + 1 :]
            else:
                print(
                    "No data in container, migrating all {} "
                    "document from local storage".format(len(transformed_data_list))
                )

        for item in tqdm(transformed_data_list, desc="Migrating to Cosmos"):
            try:
                self.container.create_item(body=item)
            except CosmosHttpResponseError as http_error:
                tqdm.write(
                    "Could not insert {} from {}. Error code: {}".format(
                        item["web_name"], item["download_time"], http_error.message
                    )
                )

    def test_transform(self, data_dir_path: str, num_of_samples=1) -> list:
        """Optional test of transformation before migrating.

        Grabs the first .json file in provided directory for testing transformation.

        Args:
            data_dir_path (str): Path to directory holding data
            num_of_samples (int, optional): Number of transformed documents to return

        Returns:
            List[dict]: List of transformed documents
        """
        dict_list = self._get_data(data_dir_path)
        return self._transform_data(dict_list[0])[:num_of_samples]

    def _get_last_insert(self) -> str:
        query = "SELECT TOP 1 * FROM c ORDER BY c._ts DESC"
        result = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        if result:
            return result[0]["id"]
        return None

    def search_db(self, query="SELECT * from c") -> list:
        """Search collectiong using SQL syntax.

        Args:
            query (str, optional): SQL query. Defaults to "SELECT * from c".

        Returns:
            list[dict]: Result of query
        """
        return list(
            self.container.query_items(
                query=query, enable_cross_partition_query=True, max_item_count=40000
            )
        )

    def get_latest_download_time(self) -> str:
        """Get timestamp of latest download.

        Returns:
            str: timestamp in format: yyyy-MM-ddTHH:mm:ss.fffffffZ
        """
        get_latest_download = "SELECT VALUE MAX(c.download_time) from c"
        return self.search_db(get_latest_download)[0]

    def get_latest_download(self) -> list:
        """Get latest download.

        Returns:
            list[dict]: List holding elements from the latest download
        """
        try:
            latest = self.get_latest_download_time()
            select_latest_query = "SELECT * from c WHERE c.download_time = '{}'".format(latest)
            return self.search_db(select_latest_query)
        except KeyError:
            print("No data in db")
            return []

    def get_latest_gameweek_number(self) -> int:
        """Get latest gameweek number.

        Returns:
            int: Number of latest downloaded gameweek
        """
        get_latest_gameweek = "SELECT VALUE MAX(c.gameweek) from c"
        return self.search_db(get_latest_gameweek)[0]

    def get_latest_gameweek(self) -> list:
        """Get elements from latest gameweek.

        Returns:
            list[dict]: List holding all elements from the latest gameweek
        """
        try:
            get_latest_gameweek = self.get_latest_gameweek_number()
            select_latest_query = "SELECT * from c WHERE c.gameweek = {}".format(
                get_latest_gameweek
            )
            return self.search_db(select_latest_query)
        except KeyError:
            print("No data in db")
            return []

    def update_one(self, document: dict):
        """Update one item in Cosmos.

        Args:
            document (dict): dict holding at least {"id": str}
        """
        self.container.upsert_item(document)

    def update_all(self, documents: list):
        """Update bulk of documents in list.

        Args:
            documents (list[dict]): List holding dicts containing at least {"id": str}
        """
        for document in tqdm(documents, desc="Updating Cosmos"):
            self.container.upsert_item(document)


class ElementsInserter(CosmoContainer):
    """Class for interacting with elements container.

    Implementation to transform "elements" from raw scraped data and read into Cosmos DB.

    """

    def _transform_data(self, dict_list: list) -> list:
        """Transform dict["elements"] to documents ready to be inserted to Cosmos DB.

        Args:
            dict_list (list[dict]): List holding raw dicts from loaded .json files downloaded
            from Azure Storage.

        Returns:
            list[dict]: list of documents ready to be inserted to Cosmos
        """
        for i in dict_list:
            gameweek = transformations.get_game_week(i["events"])
            download_time = i["download_time"]
            transformations.add_gw_and_download_time(i["elements"], download_time, gameweek)
            transformations.add_unique_id(i["elements"])
        return list(chain.from_iterable([i["elements"] for i in dict_list]))


if __name__ == "__main__":
    load_dotenv()
    test_client = ElementsInserter(
        os.getenv("AZURE_COSMOS_URI"),
        os.getenv("AZURE_COSMOS_TOKEN"),
        {"database": "fplstats", "container": "elements", "partition_key": "download_time"},
    )
