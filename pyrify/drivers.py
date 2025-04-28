from typing import Any

import sqlalchemy as sa

from pyrify.strategies import BaseStrategy


class BaseDriver:
    def __init__(self, db_uri: str):
        self.engine = self.get_db_engine(db_uri)
        self.inspector = sa.inspect(self.engine)

        if not self.inspector:
            raise ValueError("Failed to get the inspector")

        self.tables = self.inspector.get_table_names()
        self.columns = self._get_columns()
        self.quote = '"'

    def _get_columns(self) -> dict[str, dict[str, Any]]:
        result = {}

        for table in self.tables:
            result[table] = {
                column["name"]: column for column in self.inspector.get_columns(table)
            }

        return result

    def get_db_engine(self, db_uri: str) -> sa.Engine:
        """Get a SQLAlchemy engine for the given database URI

        Args:
            db_uri: The database URI

        Returns:
            An SQLAlchemy engine or None if the connection failed
        """
        engine = sa.create_engine(db_uri)

        try:
            engine.connect()
        except sa.exc.OperationalError as e:
            raise ValueError(f"Failed to connect to the database: {e}")

        return engine

    def drop_table(self, table_name: str) -> None:
        raise NotImplementedError

    def clean_table(self, table_name: str) -> None:
        raise NotImplementedError

    def update_column(
        self,
        table_name: str,
        column_name: str,
        strategy: type[BaseStrategy],
        **kwargs: Any,
    ) -> None:
        kwargs["quote"] = self.quote

        with self.engine.connect() as conn:
            rows = conn.execute(
                sa.text(
                    f"SELECT {self.quote}{column_name}{self.quote} "
                    f"FROM {self.quote}{table_name}{self.quote}"
                )
            ).fetchall()

            for row in rows:
                if row[0] is not None:
                    strategy_instance = strategy(
                        table_name, column_name, row[0], **kwargs
                    )

                    for stmt in strategy_instance.get_statements():
                        conn.execute(stmt)

            conn.commit()


class PostgresDriver(BaseDriver):
    def drop_table(self, table_name: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                sa.text(
                    f"DROP TABLE IF EXISTS {self.quote}"
                    f"{table_name}{self.quote} CASCADE"
                )
            )
            conn.commit()

    def clean_table(self, table_name: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                sa.text(
                    f"TRUNCATE TABLE {self.quote}{table_name}{self.quote} "
                    f"RESTART IDENTITY CASCADE"
                )
            )
            conn.commit()


class MySQLDriver(BaseDriver):
    def __init__(self, db_uri: str):
        super().__init__(db_uri)
        self.quote = "`"

    def drop_table(self, table_name: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                sa.text(f"DROP TABLE IF EXISTS {self.quote}{table_name}{self.quote}")
            )
            conn.commit()

    def clean_table(self, table_name: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                sa.text(f"TRUNCATE TABLE {self.quote}{table_name}{self.quote}")
            )
            conn.commit()


class SQLiteDriver(MySQLDriver):
    def __init__(self, db_uri: str):
        super().__init__(db_uri)
        self.quote = ""

    def drop_table(self, table_name: str) -> None:
        """Drop the table

        Note:
            The syntax for the DROP TABLE statement in SQLite is:

            DROP TABLE [ IF EXISTS ] table_name;
        """
        with self.engine.connect() as conn:
            conn.execute(sa.text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()

    def clean_table(self, table_name: str) -> None:
        """Clean the table by deleting all rows

        Note:
            SQLite does not have an explicit TRUNCATE TABLE command like other
            databases. To truncate a table in SQLite, you just need to execute
            a DELETE statement without a WHERE clause.
        """
        with self.engine.connect() as conn:
            conn.execute(sa.text(f"DELETE FROM {table_name}"))
            conn.commit()
