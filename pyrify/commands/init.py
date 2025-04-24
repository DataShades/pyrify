import click
import yaml

import pyrify.drivers as drivers


@click.command()
@click.option("-d", "--db-url", type=str, required=True)
def init(db_url: str):
    """Initializes the sanitize configuration"""
    driver = drivers.PostgresDriver(db_url)

    database_structure = {}

    for table in driver.tables:
        database_structure.setdefault(table, {})

        database_structure[table]["columns"] = {
            column: "~" for column in driver.columns[table]
        }

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
#
# Example that will clean the table activity:
# activity:
#   clean: true

# Example that will drop the table revision:
# revision:
#   drop: true


# You can use different strategies for each column.
# See the documentation for more information.
"""


def generate_yaml_config(database_structure: dict[str, list[str]]) -> None:
    click.echo(get_yaml_usage_comment())

    click.echo(yaml.dump(database_structure))
