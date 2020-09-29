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
@click.option("--path", "-p", type=click.Path(exists=False), default="./dump")
@click.option("--last", "-l", is_flag=True)
@click.option("--format", "-f", type=click.Choice(["json", "csv"]))
@click.pass_obj
def dump_to_csv(db_client, path, last, format):
    path = Path(path)
    if str(path.suffix) == "":
        path = Path(str(path) + "." + format)

    if last:
        df = pd.DataFrame(db_client.get_latest_download())
    else:
        df = pd.DataFrame(db_client.search_db())
    if format == "csv":
        df.to_csv(path)
    else:
        df.to_json(path, force_ascii=False, orient="records", indent=4)
