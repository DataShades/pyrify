import click

from . import init, sanitize


def get_commands() -> list[click.Command]:
    return [init.init, sanitize.sanitize]
