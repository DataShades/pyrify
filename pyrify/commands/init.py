import click
import sqlalchemy as sa


@click.command()
@click.option("--db-url", type=str, required=True)
def init(db_url: str):
    """Initializes the sanitize configuration"""
    click.echo(f"Initializing sanitize configuration for {db_url}")
    engine = sa.create_engine(db_url)

    with engine.connect() as conn:
        conn.execute(sa.text("SELECT 1"))
        click.echo("Database connected successfully")

    tables = get_tables_list(engine)

    for table in tables:
        click.echo(f"Table: {table}")

        columns = get_table_columns(engine, table)
        click.echo(f"Columns: {columns}")


def get_tables_list(engine: sa.Engine) -> list[str]:
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
    with engine.connect() as conn:
        return [
            row[0]
            for row in conn.execute(
                sa.text(
                    f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'"
                )
            ).fetchall()
        ]
