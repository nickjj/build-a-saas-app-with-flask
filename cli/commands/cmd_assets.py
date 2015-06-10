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
    return subprocess.call('npm start', shell=True)


@click.command()
def build():
    """
    Build assets to disk to the configured build path in the webpack config.
    """
    return subprocess.call('npm run-script build', shell=True)


cli.add_command(serve)
cli.add_command(build)
