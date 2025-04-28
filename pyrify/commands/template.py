import click

import pyrify.utils as utils


@click.command()
@click.option("-t", "--template-name", type=str)
def template(template_name: str | None) -> None:
    """Prints a sanitize config template to the console"""
    if template_name is None:
        click.echo(f"Available templates: {', '.join(utils.get_available_templates())}")
        return

    template = utils.get_template(template_name)

    if not template:
        click.echo(f"Template '{template_name}' not found")
        click.echo(f"Available templates: {', '.join(utils.get_available_templates())}")
        return

    click.echo(template, nl=False)
