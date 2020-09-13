import os, uuid
from typing import Container
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from dotenv import load_dotenv
import json
from pathlib import Path


class Azure_storage():
    def __init__(self, connection_string, container_name):
        self.container_name = container_name
        self.connection_string = connection_string
        self.storage_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.storage_client.get_container_client(container_name)

    def get_connection_string(self):
        return self.connection_string


    def get_container_name(self):
        return self.container_name


    def get_storage_client(self):
        return self.storage_client


    def get_container_client(self):
        return self.container_client


    def set_container(self, container_name):
        self.container_name = container_name
        self.container_client = self.storage_client.get_container_client(container_name)


    def blobs_list(self, as_list=False):
        if as_list:
            return list(self.container_client.list_blobs())
        return self.container_client.list_blobs()

    def get_blob(self, blob_name, return_json=True):
        if return_json:
            return json.loads(self.container_client.get_blob_client(blob=blob_name).download_blob().readall())
        else: 
            return self.container_client.get_blob_client(blob=blob_name).download_blob().readall()

    def get_blobs(self, return_json=True):
        if return_json:
            return [json.loads(self.container_client.get_blob_client(blob=i["name"]).download_blob().readall()) for i in self.blobs_list()]
        else: 
            return [self.container_client.get_blob_client(blob=i["name"]).download_blob().readall() for i in self.blobs_list()]

    def download_blob(self, blob_name, download_file_path="."):
        with open(Path(download_file_path, blob_name), "wb") as download_file:
            download_file.write(self.get_blob(blob_name, return_json=False))

    def download_blobs(self, download_file_path="."):
        for i in self.blobs_list():
            with open(Path(download_file_path, i["name"]), "wb") as download_file:
                download_file.write(self.get_blob(i["name"], return_json=False))
            
    def upload_blob(self, blob_name, data, is_file=False):
        if is_file:
            with open(blob_name, "rb") as data:
                self.container_client.get_blob_client(blob=blob_name).upload_blob(data)
        else:
            self.container_client.get_blob_client(blob=blob_name).upload_blob(bytes(data, 'utf-8'))

if __name__ == "__main__":
    load_dotenv()
    storage = Azure_storage(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), "fplstats")
    storage.upload_blob("test2.txt", "HELLO")