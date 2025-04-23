from pathlib import Path
from typing import Any, Callable

import sqlalchemy as sa
import yaml

import pyrify.strategy as strategy
import pyrify.types as types


def get_db_engine(db_uri: str) -> sa.Engine | None:
    """Get a SQLAlchemy engine for the given database URI

    Args:
        db_uri: The database URI

    Returns:
        An SQLAlchemy engine or None if the connection failed
    """
    engine = sa.create_engine(db_uri)

    with engine.connect() as conn:
        if not conn.execute(sa.text("SELECT 1")).fetchone():
            return None

    return engine


def get_tables_list(engine: sa.Engine) -> list[str]:
    """Get the list of tables in the database

    Args:
        engine: The SQLAlchemy engine to use

    Returns:
        A list of table names
    """
    with engine.connect() as conn:
        return [
            row[0]
            for row in conn.execute(
                sa.text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                )
            ).fetchall()
        ]


def get_table_columns(engine: sa.Engine, table_name: str) -> list[str]:
    """Get the list of columns in a table

    Args:
        engine: The SQLAlchemy engine to use
        table_name: The name of the table to get the columns of

    Returns:
        A list of column names
    """
    with engine.connect() as conn:
        return [
            row[0]
            for row in conn.execute(
                sa.text(
                    f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'"
                )
            ).fetchall()
        ]


def drop_table(engine: sa.Engine, table_name: str) -> None:
    with engine.connect() as conn:
        conn.execute(sa.text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
        conn.commit()


def clean_table(engine: sa.Engine, table_name: str) -> None:
    with engine.connect() as conn:
        conn.execute(sa.text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE'))
        conn.commit()


def update_column(
    engine: sa.Engine, table_name: str, column_name: str, strategy: Callable[[Any], str]
) -> None:

    with engine.connect() as conn:
        rows = conn.execute(
            sa.text(f'SELECT "{column_name}" FROM "{table_name}"')
        ).fetchall()

        for row in rows:
            if row[0] is not None:
                conn.execute(
                    sa.text(
                        f'UPDATE "{table_name}" '
                        f'SET "{column_name}" = {strategy(row[0])} '
                        f"WHERE \"{column_name}\" = '{row[0]}'"
                    )
                )

        conn.commit()


def load_config(config_path: Path) -> types.SanitizeConfig:
    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    sanitize_config = types.SanitizeConfig()

    for table, config in raw_config.items():
        sanitize_config.tables[table] = types.TableConfig(**config)

    return sanitize_config


def get_strategy(strategy_name: str) -> Callable[[str], str]:
    """Get a strategy function by its name

    Args:
        strategy_name: The name of the strategy to get

    Returns:
        A strategy function
    """
    strategies = strategy.get_strategies()
    if strategy_name not in strategies:
        raise ValueError(f"Invalid strategy: {strategy_name}")

    return strategies[strategy_name]
