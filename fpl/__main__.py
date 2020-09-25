"""Main module."""

import os

import pandas as pd
from dotenv import load_dotenv

from fpl.data.azure_storage import AzureStorage
from fpl.data.cosmos import ElementsInserter

load_dotenv()
# Creates connection to storage account
storage = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "fplstats")
# storage.download_new_blobs(Path(Path(__file__).resolve().parents[1], "data"))
test_client = ElementsInserter(
    os.getenv("AZURE_COSMOS_URI"),
    os.getenv("AZURE_COSMOS_TOKEN"),
    {"database": "fplstats", "container": "test_elements", "partition_key": "download_time"},
)


print(test_client.get_latest_gameweek()[:1])
