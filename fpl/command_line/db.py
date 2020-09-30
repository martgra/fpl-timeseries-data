"""Interaction with Cosmos DB through CLI."""
import os
from pathlib import Path

import click
import pandas as pd

from fpl.data.cosmos import ElementsInserter


@click.group(help="Procedures to interact with Azure Cosmos DB", name="cosmos")
@click.pass_context
def cosmos_cli(ctx):
    """Download group."""
    db_client = ElementsInserter(
        os.getenv("AZURE_COSMOS_URI"),
        os.getenv("AZURE_COSMOS_TOKEN"),
        {"database": "fplstats", "container": "elements", "partition_key": "download_time"},
    )
    ctx.obj = db_client


@cosmos_cli.command(name="dump")
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=False),
    default="./dump",
    help="File path to where to write data dump",
)
@click.option("--last", "-l", is_flag=True, help="Get data with last timestamp")
@click.option(
    "--format-type",
    "-f",
    type=click.Choice(["json", "csv"]),
    help="Choose format in which to dump data",
)
@click.pass_obj
def dump(db_client, path, last, format_type):
    """Dump all or latest data."""
    path = Path(path)
    if str(path.suffix) == "":
        path = Path(str(path) + "." + format)

    if last:
        dataframe = pd.DataFrame(db_client.get_latest_download())
    else:
        dataframe = pd.DataFrame(db_client.search_db())
    if format_type == "csv":
        dataframe.to_csv(path)
    else:
        dataframe.to_json(path, force_ascii=False, orient="records", indent=4)
