"""Implmentation of Azure connection."""
import json
import os
from pathlib import Path
from typing import List

from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
from tqdm import tqdm


class AzureStorage:
    """Azure Storage Blob class.

    Attributes:
        container_name (str): The name of the connected container
        storage_client (azure.storage.blob.BlobServiceClient): Storage account client
        container_client (azure.storage.blob.ContainerClient): Container client

    Example:
        load_dotenv()
        storage = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "fplstats")
        storage.download_new_blobs(Path(Path(__file__).resolve().parents[1], "data"))
    """

    def __init__(self, connection_string: str, container_name: str):
        """Initialize object.

        Args:
            connection_string (str): Connection string for the storage container
            container_name (str): Name of the container to connect to
        """
        self.container_name = container_name
        try:
            self.storage_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_client = self.storage_client.get_container_client(container_name)
            self.storage_client.get_service_stats()
        except:
            self.storage_client = None
            self.container_client = ContainerClient.from_container_url(connection_string)
            print("Read Access only")

    def get_storage_client(self) -> BlobServiceClient:
        """Return the Storage Blob client.

        Returns:
            azure.storage.blob.BlobServiceClient: client to the current storage account
        """
        return self.storage_client

    def get_container_client(self):
        """Return the Container client.

        Returns:
            azure.storage.blob.ContainerClient: client for the current container
        """
        return self.container_client

    def set_container(self, container_name: str):
        """Change container within the storage account.

        Args:
            container_name (str): Set new container
        """
        self.container_name = container_name
        self.container_client = self.storage_client.get_container_client(container_name)

    def blobs_list(self, as_list=False) -> List[str]:
        """Return list of all blobs in container.

        Args:
            as_list (bool, optional): If true returns a list of names of blobs as str.
                Defaults to False.

        Returns:
            list[str]: List holding all blobs in container wither as str
                or azure.core.paging.ItemPaged[~azure.storage.blob.BlobProperties]
        """
        if as_list:
            return [i["name"] for i in self.container_client.list_blobs()]
        return self.container_client.list_blobs()

    def get_blob(self, blob_name) -> dict:
        """Return content of specific blob.

        Args:
            blob_name (str): Name of the blob to get

        Returns:
            bytes: Content of blob in bytes
        """
        return json.loads(
            self.container_client.get_blob_client(blob=blob_name).download_blob().readall()
        )

    def get_blobs(self) -> List[dict]:
        """Get all blobs in container.

        Args:
            return_json (bool, optional): Returns json instead of string. Defaults to True.

        Returns:
            list[dict]: returns list of dicts
        """
        return [
            json.loads(
                self.container_client.get_blob_client(blob=i["name"]).download_blob().readall()
            )
            for i in self.blobs_list()
        ]

    def download_blob(self, blob_name: str, download_file_path="."):
        """Download a single blob to disk.

        Args:
            blob_name (str): Name of blob to download
            download_file_path (str, optional): Path to dir to download to. Defaults to ".".
        """
        with open(Path(download_file_path, blob_name), "w") as download_file:
            json.dump(self.get_blob(blob_name), download_file, indent=4, ensure_ascii=False)

    def download_blobs(self, download_dir_path="."):
        """Download all blobs in container to disk.

        Args:
            download_file_path (str, optional): Path to dir to download to. Defaults to ".".
        """
        for i in tqdm(self.blobs_list(), desc="Downloading all blobs"):
            with open(Path(download_dir_path, i["name"]), "w", encoding="utf8") as download_file:
                json.dump(self.get_blob(i["name"]), download_file, indent=4, ensure_ascii=False)

    def download_new_blobs(self, download_dir_path="data"):
        """Download new blobs that does not exsist in destination.

        Args:
            download_dir_path (str, optional): Path to directory to download to. Defaults to "data".
        """
        try:
            allready_on_disk = os.listdir(download_dir_path)
            to_download = [i for i in self.blobs_list(as_list=True) if i not in allready_on_disk]
            for i in tqdm(to_download, desc="Downloading new blobs"):
                with open(Path(download_dir_path, i), "w", encoding="utf8") as download_file:
                    json.dump(self.get_blob(i), download_file, ensure_ascii=False, indent=4)
        except OSError as error:
            print("Check that path points to a dir. {}".format(error))

    def upload_blob(self, blob_name: str, data=None, is_file=False, overwrite=False):
        """Upload data to blob.

        Args:
            blob_name (str): Name of the local file and to-be-blob
            data (str, optional): Data to upload to blob. Defaults to None.
            is_file (bool, optional): Upload local file instad of in-memory data. Defaults to False.
        """
        if is_file:
            with open(blob_name) as data:
                self.container_client.get_blob_client(blob=Path(blob_name).name).upload_blob(
                    json.dumps(json.load(data), indent=4, ensure_ascii=False), overwrite=overwrite
                )
        else:
            self.container_client.get_blob_client(blob=blob_name).upload_blob(
                json.dumps(data, indent=4, ensure_ascii=False)
            )

    def delete_blob(self, blob_name, delete_snapshots=False):
        """Delete blob.

        Args:
            blob_name (str): Name of blob to delete
            delete_snapshots (bool, optional): To completely delete blob set true.
                Defaults to False.
        """
        self.container_client.get_blob_client(blob=blob_name).delete_blob(
            delete_snapshots=delete_snapshots
        )


if __name__ == "__main__":
    # Loads connection string from .env file in current dir
    # Connection string needs to be added to .env
    # file or passed directly as its out of version control
    load_dotenv()

    # Creates connection to storage account
    storage = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "fplstats")
