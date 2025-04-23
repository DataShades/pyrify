import click
import yaml

import pyrify.utils as utils


@click.command()
@click.option("-d", "--db-url", type=str, required=True)
def init(db_url: str):
    """Initializes the sanitize configuration"""
    engine = utils.get_db_engine(db_url)

    if not engine:
        raise click.ClickException("Database connection failed")
    database_structure = {}

    for table in utils.get_tables_list(engine):
        database_structure.setdefault(table, {})

        database_structure[table]["columns"] = [
            {column: "~"} for column in utils.get_table_columns(engine, table)
        ]

    generate_yaml_config(database_structure)


def get_yaml_usage_comment() -> str:
    return """
# This is a YAML configuration file for the pyrify tool.
# It describes the tables and the columns that should be sanitized.

# You can delete the table from the list to keep it as is.
# You can delete the column from the list to keep it as is.

# You can use the following commands relative to the table name:
# - clean: clean the table
# - drop: drop the table

# You can use different strategies for each column:
# - nullify: set the column to null
# - fake_name: set the column to a fake name
# - fake_email: set the column to a fake email
# - fake_password: set the column to a fake password
"""


def generate_yaml_config(database_structure: dict[str, list[str]]) -> None:
    click.echo(get_yaml_usage_comment())

    click.echo(yaml.dump(database_structure))
