from fpl.data.azure_storage import Azure_storage
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv()

# Creates connection to storage account
storage = Azure_storage(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), "fplstats")
try:
    storage.download_new_blobs(Path(Path(__file__).resolve().parents[1], "data"))
    
except:
    raise