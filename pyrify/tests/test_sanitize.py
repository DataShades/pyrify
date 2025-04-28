import os

import pytest
import sqlalchemy as sa
from dotenv import load_dotenv

import pyrify.drivers as drivers
import pyrify.utils as utils
from pyrify.tests.models import Base, Revision, Session, User, get_json_type
from pyrify.types import SanitizeConfig, TableConfig
from pyrify.utils import get_driver

load_dotenv()


class CustomSQLiteDriver(drivers.SQLiteDriver):
    def __init__(self, engine: sa.Engine):
        self.engine = engine
        self.inspector = sa.inspect(self.engine)

        if not self.inspector:
            raise ValueError("Failed to get the inspector")

        self.tables = self.inspector.get_table_names()
        self.columns = self._get_columns()
        self.quote = '"'


@pytest.fixture(
    params=[
        os.environ.get("DB_URI_POSTGRES"),
        os.environ.get("DB_URI_MYSQL"),
        os.environ.get("DB_URI_SQLITE"),
    ]
)
def driver(request):
    """Initialize the database, create tables, and yield a driver."""

    db_uri = request.param

    engine = sa.create_engine(db_uri)

    # # Adjust JSON/JSONB type if necessary
    User.__table__.columns.user_extras.type = get_json_type(engine.name)()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)

    with engine.connect() as conn:
        conn.execute(
            sa.insert(User.__table__).values(
                [
                    {
                        "id": 1,
                        "name": "Alice",
                        "email": "alice@example.com",
                        "phone": "1234567890",
                        "address": "123 St",
                        "about": "XXX",
                        "user_extras": {"secret": "bar", "foo": "bar"},
                    }
                ]
            )
        )
        conn.execute(
            sa.insert(Session.__table__).values(
                [{"session_id": "abc123"}, {"session_id": "def456"}]
            )
        )
        conn.execute(
            sa.insert(Revision.__table__).values(
                [{"id": 1, "data": "test"}, {"id": 2, "data": "test"}]
            )
        )
        conn.commit()

    driver = get_driver_for_db_uri(db_uri)

    yield driver

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def sanitize_config() -> SanitizeConfig:
    return SanitizeConfig(
        tables={
            "session": TableConfig(clean=True),
            "revisions": TableConfig(drop=True),
            "user": TableConfig(
                columns={
                    "name": "fake_username",
                    "email": "fake_email",
                    "phone": "fake_phone_number",
                    "address": "fake_address",
                    "about": "fake_text",
                    "user_extras": {
                        "strategy": "json_update",
                        "kwargs": {
                            "columns": {
                                "secret": "fake_password",
                            }
                        },
                    },
                }
            ),
        }
    )


def get_driver_for_db_uri(db_uri: str) -> drivers.BaseDriver:
    return get_driver(db_uri)


class TestSanitize:
    def test_sanitize_db(self, driver, sanitize_config: SanitizeConfig):
        inspector = sa.inspect(driver.engine)

        with driver.engine.connect() as conn:
            result = conn.execute(sa.text("SELECT * FROM session;"))
            assert result.fetchall() == [("abc123",), ("def456",)]

            result = conn.execute(sa.text("SELECT * FROM revisions;"))
            assert result.fetchall() == [(1, "test"), (2, "test")]

            result = conn.execute(User.all())

            assert result.fetchall() == [
                (
                    1,
                    "Alice",
                    "alice@example.com",
                    "1234567890",
                    "123 St",
                    "XXX",
                    {"secret": "bar", "foo": "bar"},
                )
            ]

        utils.sanitize_db(driver, sanitize_config)

        with driver.engine.connect() as conn:
            result = conn.execute(sa.text("SELECT * FROM session;"))

            assert result.fetchall() == []
            assert not inspector.has_table("revisions")

            result = conn.execute(User.all())

            users = result.fetchall()
            user = users[0]

            # id is not changed
            assert user[0] == 1

            # sensitive data is changed
            assert user[1] != "Alice"
            assert user[2] != "alice@example.com"
            assert user[3] != "1234567890"
            assert user[4] != "123 St"
            assert user[5] != "XXX"

            # other data is not changed, only secret key is changed
            assert user[6]["foo"] == "bar"
            assert user[6]["secret"] != "bar"
