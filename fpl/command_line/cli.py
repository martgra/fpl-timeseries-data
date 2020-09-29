"""Application CLI."""
import click
from dotenv import load_dotenv

from fpl.command_line.db import cosmos_cli
from fpl.command_line.storage import storage


@click.group(help="FPL cli")
def cli():
    """CLI function."""
    load_dotenv()


def register_cli():
    """Sow everything together."""
    cli.add_command(storage)
    cli.add_command(cosmos_cli)
    cli()
