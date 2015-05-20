import subprocess

import click


@click.group()
def cli():
    """ Serve and build assets. """
    pass


@click.command()
def serve():
    """
    Serve assets in development.
    """
    subprocess.call('npm start', shell=True)


@click.command()
def build():
    """
    Build assets for production.
    """
    subprocess.call('npm run-script build', shell=True)


cli.add_command(serve)
cli.add_command(build)
