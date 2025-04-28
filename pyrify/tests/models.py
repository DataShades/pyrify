import sqlalchemy as sa
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_json_type(engine_name: str) -> type[sa.JSON]:
    """Returns the appropriate JSON type based on the database backend."""
    if engine_name == "postgresql":
        return JSONB
    elif engine_name == "mysql":
        return MySQLJSON
    else:
        # return sa.JSON  # SQLite fallback (SQLAlchemy 1.4+ has JSON for SQLite too)
        return SQLiteJSON


# def create_all_tables(engine):
#     json_type = get_json_type(engine)
#     User.__table__.columns.user_extras.type = json_type

#     Base.metadata.create_all(bind=engine)


class Session(Base):
    __tablename__ = "session"

    session_id = sa.Column(sa.String(255), primary_key=True)


class User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255))
    email = sa.Column(sa.String(255))
    phone = sa.Column(sa.String(255))
    address = sa.Column(sa.String(255))
    about = sa.Column(sa.String(255))
    user_extras = sa.Column(sa.JSON)

    @classmethod
    def all(cls):
        return sa.select(cls)


class Revision(Base):
    __tablename__ = "revisions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    data = sa.Column(sa.String(255))
