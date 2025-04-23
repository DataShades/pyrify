import click

from . import init


def get_commands() -> list[click.Command]:
    return [init.init]
