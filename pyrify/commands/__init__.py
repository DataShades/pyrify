import click

from . import init, sanitize, template


def get_commands() -> list[click.Command]:
    return [
        init.init,
        sanitize.sanitize,
        template.template,
    ]
