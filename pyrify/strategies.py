import hashlib
import json
from typing import Any

import sqlalchemy as sa
from faker import Faker

fake = Faker()


class BaseStrategy:
    def __init__(self, table_name: str, column_name: str, value: Any, **kwargs: Any):
        self.table_name = table_name
        self.column_name = column_name
        self.value = value
        self.kwargs = kwargs
        self.fake = fake

    def get_value(self) -> Any:
        raise NotImplementedError

    def get_statements(self) -> list[sa.TextClause]:
        new_value = self.get_value()
        q = self.kwargs["quote"]
        return [
            sa.text(
                f"UPDATE {q}{self.table_name}{q} "
                f"SET {q}{self.column_name}{q} = '{new_value}'"
                f"WHERE {q}{self.column_name}{q} = '{self.value}'"
            )
        ]


class UsernameStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.unique.user_name()


class FullnameStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.unique.name()


class EmailStrategy(BaseStrategy):
    def get_value(self) -> str:
        hash_value = hashlib.md5(self.value.encode()).hexdigest()
        return f"{hash_value}@pyrify.com"


class TextStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.text()


class PasswordStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.password(length=16)


class PhoneNumberStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.phone_number()


class AddressStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.address()


class ImageUrlStrategy(BaseStrategy):
    def get_value(self) -> str:
        return self.fake.image_url()


class NullifyStrategy(BaseStrategy):
    def get_statements(self) -> list[sa.TextClause]:
        q = self.kwargs["quote"]

        return [
            sa.text(
                f"UPDATE {q}{self.table_name}{q} "
                f"SET {q}{self.column_name}{q} = NULL "
                f"WHERE {q}{self.column_name}{q} = '{self.value}'"
            )
        ]


class JsonCleanStrategy(BaseStrategy):
    def get_statements(self) -> list[sa.TextClause]:
        from pyrify.utils import get_strategy

        statements = []

        for key, strategy in self.kwargs.get("columns", {}).items():
            strategy_class = get_strategy(strategy, self.kwargs["engine_name"])

            if not strategy_class:
                raise ValueError(f"Strategy {strategy} not found")

            strategy_instance = strategy_class(
                self.table_name, self.column_name, self.value
            )
            new_value = strategy_instance.get_value()

            statements.append(self.update_json_value(key, new_value))

        return statements

    def update_json_value(self, key: str, new_value: Any) -> sa.TextClause:
        raise NotImplementedError


class PostgresJsonCleanStrategy(JsonCleanStrategy):
    def update_json_value(self, key: str, new_value: Any) -> sa.TextClause:
        return sa.text(
            f'UPDATE "{self.table_name}" '
            f"SET {self.column_name} = jsonb_set({self.column_name}, "
            f"'{{\"{key}\"}}', '{json.dumps(new_value)}'::jsonb) "
            f"WHERE \"{self.column_name}\" = '{json.dumps(self.value)}'::jsonb"
        )


class MySQLJsonCleanStrategy(JsonCleanStrategy):
    def update_json_value(self, key: str, new_value: Any) -> sa.TextClause:
        json_path = f"$.{key}"

        query = sa.text(
            f"UPDATE `{self.table_name}` "
            f"SET `{self.column_name}` = JSON_SET({self.column_name}, "
            f"'{json_path}', {json.dumps(new_value)}) "
            f"WHERE JSON_UNQUOTE(JSON_EXTRACT(`{self.column_name}`, '$')) = "
            f"{json.dumps(self.value)}"
        )

        return query


class SQLiteJsonCleanStrategy(JsonCleanStrategy):
    def update_json_value(self, key: str, new_value: Any) -> sa.TextClause:
        return sa.text(
            f"UPDATE {self.table_name} "
            f"SET {self.column_name} = json_set("
            f"{self.column_name}, '$.{key}', '{new_value}') "
            f"WHERE json({self.column_name}) = json('{self.value}')"
        )


def get_strategies(engine_name: str) -> dict[str, type[BaseStrategy]]:
    common_strategies = {
        "fake_username": UsernameStrategy,
        "fake_fullname": FullnameStrategy,
        "fake_text": TextStrategy,
        "fake_email": EmailStrategy,
        "fake_password": PasswordStrategy,
        "fake_phone_number": PhoneNumberStrategy,
        "fake_address": AddressStrategy,
        "nullify": NullifyStrategy,
    }

    if engine_name == "postgresql":
        common_strategies["json_update"] = PostgresJsonCleanStrategy
    elif engine_name == "mysql":
        common_strategies["json_update"] = MySQLJsonCleanStrategy
    elif engine_name == "sqlite":
        common_strategies["json_update"] = SQLiteJsonCleanStrategy

    return common_strategies
