"""Main module."""

import os

from dotenv import load_dotenv

from fpl.data.azure_storage import AzureStorage
from fpl.data.cosmos import ElementsInserter

load_dotenv()
# Creates connection to storage account
storage = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "fplstats")
# storage.download_new_blobs(Path(Path(__file__).resolve().parents[1], "data"))
# test_client = ElementsInserter(
#     os.getenv("AZURE_COSMOS_URI"),
#     os.getenv("AZURE_COSMOS_TOKEN"),
#     {"database": "fplstats", "container": "test_elements", "partition_key": "download_time"},
# )

# # test_client.insert_documents("/home/jason/dev/fpl2021/data", latest=True)
# print(test_client.test_transform("/home/jason/dev/fpl2021/data", num_of_samples=2))
# storage.upload_blob(
#     "test.json",
#     data="/home/jason/dev/fpl2021/data/2020-09-24T06-00-00Z_data.json",
#     is_file=True,
#     overwrite=True,
# )
storage.download_new_blobs("/home/jason/dev/fpl2021/data")
