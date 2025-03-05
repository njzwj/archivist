import click

from .init import init as init_command
from .debug import debug as debug_command
from .get import get as get_command


@click.group()
def cli():
    """Archivist CLI tool for managing archives"""
    pass


@cli.command()
def init():
    """Initialize the archivist environment"""
    init_command()


@cli.command()
@click.argument("url", required=True, type=str)
def get(url):
    """Download a video/webpage from url to archive"""
    get_command(url)


@cli.command()
@click.argument("url", required=True, type=str)
def debug(url):
    """Debug a video download from url"""
    debug_command(url)


def main():
    cli()


if __name__ == "__main__":
    main()
