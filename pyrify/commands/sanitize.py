from pathlib import Path

import click

import pyrify.utils as utils

POTENTIAL_SENSITIVE_COLUMNS = [
    "password",
    "image_url",
    "email",
    "name",
    "fullname",
    "secret",
]
CKAN_SENSITIVE_TABLES = ["user", "api_token", "activity"]


@click.command()
@click.option("-d", "--db-uri", type=str, required=True)
@click.option("-c", "--config", type=click.Path(exists=True), required=True)
def sanitize(db_uri: str, config: Path) -> None:
    """Sanitizes the database"""

    sanitize_config = utils.load_config(config)
    engine = utils.get_db_engine(db_uri)

    if not engine:
        raise click.ClickException("Database connection failed")

    for table, table_config in sanitize_config.tables.items():
        if table not in utils.get_tables_list(engine):
            click.echo(f"Table {table} not found. Skipping...")
            continue

        if table_config.clean:
            click.echo(f"Cleaning table {table}...")
            utils.clean_table(engine, table)
            continue

        if table_config.drop:
            click.echo(f"Dropping table {table}...")
            utils.drop_table(engine, table)
            continue

        if not table_config.columns:
            continue

        for column in table_config.columns:
            column_name, strategy = next(iter(column.items()))

            if column_name not in utils.get_table_columns(engine, table):
                click.echo(
                    f"Column {column_name} for table {table} not found. Skipping..."
                )
                continue

            click.echo(
                f"Updating column {column_name} for table {table} with strategy {strategy}..."
            )

            utils.update_column(
                engine, table, column_name, utils.get_strategy(strategy)
            )
