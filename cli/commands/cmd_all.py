import subprocess

import click


@click.command()
def cli():
    """ Start all services. """
    cmd = 'honcho start'
    subprocess.call(cmd, shell=True)
