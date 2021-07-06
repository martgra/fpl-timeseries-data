"""CLI Storage module."""

import os
from pathlib import Path

import click

from fpl.data.azure_storage import AzureStorage
from fpl.data.transformations import to_csv

DEFAULT_STORAGE_ACCOUNT = "https://martinfplstats1337.blob.core.windows.net"
DEFAULT_CONTAINER = "2020-fpl-data"


@click.group(help="Procedures to download data from Azure Blob Storage")
@click.option("--connection-string", "-c", type=str, default=None)
@click.option("--container", type=str, default=DEFAULT_CONTAINER)
@click.pass_context
def storage(ctx, connection_string, container):
    """Download group."""
    try:
        if connection_string:
            storage_client = AzureStorage(connection_string, container)
        else:
            storage_client = AzureStorage(
                os.getenv("AZURE_STORAGE_CONNECTION_STRING") or DEFAULT_STORAGE_ACCOUNT, container
            )
        ctx.obj = storage_client
    except TypeError:
        print("ERROR IN CONNECTION STRING")


@storage.command(name="download-all", help="Download multiple blobs to local storage")
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(),
    default=lambda: Path("data", "raw", click.get_current_context().parent.params["container"]),
    help="Path to dir to store blobs",
)
@click.option(
    "--download-all",
    "-a",
    is_flag=True,
    help="If passed, will download all blobs from Azure, not just new",
)
@click.pass_obj
def download_bulk(storage_client, data_dir, download_all):
    """Download many blobs to local storage."""
    data_dir.mkdir(exist_ok=True, parents=True)
    if download_all:
        storage_client.download_blobs(download_dir_path=data_dir)
    else:
        storage_client.download_new_blobs(download_dir_path=data_dir)


@storage.command(name="download-one", help="Download multiple blobs to local storage")
@click.option("--blob-name", "-n", type=str, help="Name of blob in azure")
@click.option(
    "--data-dir", "-d", type=click.Path(exists=True), help="Path to directory to store blob"
)
@click.pass_obj
def download_one(storage_client, blob_name, data_dir):
    """Download one blob to local storage."""
    storage_client.download_blob(blob_name, data_dir)


@storage.command(name="list", help="List content of storage container")
@click.pass_obj
def list_storage(storage_client):
    """List blobs in Azure Storage."""
    for blob in storage_client.blobs_list(as_list=True):
        print(blob)


@storage.command(name="to-csv", help="Transform JSON files in /data and save as CSV")
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(exists=True),
    help="Path to directory that holds JSON",
    default=lambda: Path("data", click.get_current_context().parent.params["container"]),
)
@click.option(
    "--save",
    "-s",
    type=click.Path(),
    help="Path to save CSV",
    default="data/transformed/transformed.csv",
)
def json_to_csv(data_dir, save):
    """Transform all JSON in dir and save as CSV."""
    csv_data = to_csv(data_dir)
    Path(save).parent.mkdir(exist_ok=True, parents=True)
    csv_data.to_csv(save)
