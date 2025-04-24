from pathlib import Path

import click

import pyrify.utils as utils


@click.command()
@click.option("-d", "--db-uri", type=str, required=True)
@click.option("-c", "--config", type=click.Path(exists=True), required=True)
def sanitize(db_uri: str, config: Path) -> None:
    """Sanitizes the database"""

    utils.sanitize_db(utils.get_driver(db_uri), utils.load_config(config))
