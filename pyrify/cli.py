import click

from pyrify.commands import get_commands


@click.group()
def main():
    """Pyrify - A CLI tool for database sanitization."""
    pass


# Register commands
for command in get_commands():
    main.add_command(command)

if __name__ == "__main__":
    main()
