"""Application CLI."""

import os

import click
from dotenv import load_dotenv

from fpl.data.azure_storage import AzureStorage


@click.group(help="FPL cli")
def cli():
    """CLI function."""
    load_dotenv()


@click.group(help="Procedures to download data from Azure Blob Storage")
@click.pass_context
def storage(ctx):
    """Download group."""
    storage_client = AzureStorage(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "fplstats")
    ctx.obj = storage_client


@storage.command(name="download-all", help="Download multiple blobs to local storage")
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(exists=True),
    default="data",
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


def main():
    """Entry."""
    cli.add_command(storage)
    cli()


if __name__ == "__main__":
    main()
