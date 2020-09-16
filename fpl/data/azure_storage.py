"""Implmentation of Azure connection"""
import os, uuid
from typing import Container
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from dotenv import load_dotenv
import json
from pathlib import Path


class Azure_storage():
    """ Azure Storage Blob object"""    
    def __init__(self, connection_string, container_name):
        self.container_name = container_name
        self.connection_string = connection_string
        self.storage_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.storage_client.get_container_client(container_name)

    def get_connection_string(self):
        """Return the connection string

        Returns:
            str: The Azure Connection
        """        
        return self.connection_string


    def get_container_name(self):
        """Get the current container name

        Returns:
            str: Returns the name of the current container
        """        
        return self.container_name


    def get_storage_client(self):
        """Return the Storage Blob client

        Returns:
            BlobServiceClient: client to the current storage account
        """        
        return self.storage_client


    def get_container_client(self):
        """Return the Container client

        Returns:
            ContainerClient: client for the current container
        """        
        return self.container_client


    def set_container(self, container_name):
        """Change container within the storage account

        Args:
            container_name (str): Set new container
        """        
        self.container_name = container_name
        self.container_client = self.storage_client.get_container_client(container_name)


    def blobs_list(self, as_list=False):
        """Return list of all blobs in container

        Args:
            as_list (bool, optional): If true returns a list of names of blobs as str. Defaults to False.

        Returns:
            list: List holding all blobs in container
        """        
        if as_list:
            return [i["name"] for i  in self.container_client.list_blobs()]
        return self.container_client.list_blobs()


    def get_blob(self, blob_name, return_json=True):
        """Returns content of specific blob

        Args:
            blob_name (str): Name of the blob to get
            return_json (bool, optional): Returns the blob as json. Defaults to True.

        Returns:
            json: Content of blob
        """        
        if return_json:
            return json.loads(self.container_client.get_blob_client(blob=blob_name).download_blob().readall())
        else: 
            return self.container_client.get_blob_client(blob=blob_name).download_blob().readall()


    def get_blobs(self, return_json=True):
        """Gets all blobs in container

        Args:
            return_json (bool, optional): Returns json instead of string. Defaults to True.

        Returns:
            list: returns list of either str og json
        """        
        if return_json:
            return [json.loads(self.container_client.get_blob_client(blob=i["name"]).download_blob().readall()) for i in self.blobs_list()]
        else: 
            return [self.container_client.get_blob_client(blob=i["name"]).download_blob().readall() for i in self.blobs_list()]


    def download_blob(self, blob_name, download_file_path="."):
        """Downloads blob to disk

        Args:
            blob_name (str): Name of blob to download
            download_file_path (str, optional): Path to dir to download to. Defaults to ".".
        """        
        with open(Path(download_file_path, blob_name), "wb") as download_file:
            download_file.write(self.get_blob(blob_name, return_json=False))

    def download_blobs(self, download_file_path="."):
        """Download all blobs in container

        Args:
            download_file_path (str, optional): Path to dir to download to. Defaults to ".".
        """        
        for i in self.blobs_list():
            with open(Path(download_file_path, i["name"]), "wb") as download_file:
                download_file.write(self.get_blob(i["name"], return_json=False))
            
    def upload_blob(self, blob_name, data=None, is_file=False):
        """Upload data to blob

        Args:
            blob_name (str): Name of the local file and to-be-blob
            data (str, optional): Data to upload to blob. Defaults to None.
            is_file (bool, optional): Upload local file instad of in-memory data. Defaults to False.
        """        
        if is_file:
            with open(blob_name, "rb") as data:
                self.container_client.get_blob_client(blob=blob_name).upload_blob(data)
        else:
            self.container_client.get_blob_client(blob=blob_name).upload_blob(bytes(data, 'utf-8'))


    def delete_blob(self, blob_name, delete_snapshots=False):
        """Delete blob

        Args:
            blob_name (str): Name of blob to delete
            delete_snapshots (bool, optional): To completely delete blob set true. Defaults to False.
        """        
        self.container_client.get_blob_client(blob=blob_name).delete_blob(delete_snapshots=delete_snapshots)

if __name__ == "__main__":
    # Loads connection string from .env file in current dir
    # Connection string needs to be added to .env file or passed directly as its out of version control
    load_dotenv()

    # Creates connection to storage account
    storage = Azure_storage(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), "fplstats")
    storage.download_blobs("/home/vagrant/dev/fpl2021/data")