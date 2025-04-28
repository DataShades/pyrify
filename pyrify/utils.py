from pathlib import Path

import click
import yaml

import pyrify.types as types
from pyrify.drivers import BaseDriver, MySQLDriver, PostgresDriver, SQLiteDriver
from pyrify.strategies import BaseStrategy, get_strategies


def load_config(config_path: Path) -> types.SanitizeConfig:
    """Load the sanitize configuration from a YAML file

    Args:
        config_path: The path to the YAML file

    Returns:
        A sanitize configuration
    """
    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    sanitize_config = types.SanitizeConfig()

    for table, config in raw_config.items():
        sanitize_config.tables[table] = types.TableConfig(**config)

    return sanitize_config


def get_strategy(strategy_name: str, engine_name: str) -> type[BaseStrategy]:
    """Get a strategy function by its name

    Args:
        strategy_name: The name of the strategy to get

    Returns:
        A strategy function
    """
    strategies = get_strategies(engine_name)

    if strategy_name not in strategies:
        raise ValueError(f"Invalid strategy: {strategy_name}")

    return strategies[strategy_name]


def get_driver(db_uri: str) -> BaseDriver:
    """Get a driver for the given database URI

    Args:
        db_uri: The database URI

    Returns:
        A database driver
    """
    if db_uri.startswith("postgres"):
        return PostgresDriver(db_uri)
    elif db_uri.startswith("mysql"):
        return MySQLDriver(db_uri)
    elif db_uri.startswith("sqlite"):
        return SQLiteDriver(db_uri)
    else:
        raise ValueError(f"Unsupported database URI: {db_uri}")


def sanitize_db(driver: BaseDriver, sanitize_config: types.SanitizeConfig) -> None:
    for table, table_config in sanitize_config.tables.items():
        if table not in driver.tables:
            click.echo(f"Table {table} not found. Skipping...")
            continue

        if table_config.clean:
            click.echo(f"Cleaning table {table}...")
            driver.clean_table(table)
            continue

        if table_config.drop:
            click.echo(f"Dropping table {table}...")
            driver.drop_table(table)
            continue

        if not table_config.columns:
            continue

        for column_name, strategy in table_config.columns.items():
            if column_name not in driver.columns[table]:
                click.echo(
                    f"Column {column_name} for table {table} not found. Skipping..."
                )
                continue

            click.echo(
                f"Updating column {column_name} for table {table} with strategy {strategy}..."
            )

            # Handle nested strategies
            if isinstance(strategy, dict):
                strategy_name = strategy["strategy"]
                strategy_kwargs = strategy.pop("kwargs", {})
                strategy_kwargs["engine_name"] = driver.engine.name
            else:
                strategy_name = strategy
                strategy_kwargs = {}

            driver.update_column(
                table,
                column_name,
                get_strategy(strategy_name, driver.engine.name),
                **strategy_kwargs,
            )
