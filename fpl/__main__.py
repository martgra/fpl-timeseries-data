"""Main module."""

import os
from pathlib import Path

from dotenv import load_dotenv

from fpl.data.azure_storage import AzureStorage
from fpl.data.cosmos import ElementsInserter

load_dotenv()
# Creates connection to storage account
storage = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "fplstats")
test_client = ElementsInserter(
    os.getenv("AZURE_COSMOS_URI"),
    os.getenv("AZURE_COSMOS_TOKEN"),
    {"database": "fplstats", "container": "elements", "partition_key": "download_time"},
)

# Uncomment for examples of function
# storage.download_new_blobs(Path(Path(__file__).resolve().parents[1], "data"))
# print(test_client.get_latest_gameweek()[:1])
test_client.update_db()
