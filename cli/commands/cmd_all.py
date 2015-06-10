import subprocess

import click


@click.command()
def cli():
    """ Start all services. """
    cmd = 'honcho start'
    return subprocess.call(cmd, shell=True)
