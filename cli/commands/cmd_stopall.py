import subprocess

import click


@click.command()
def cli():
    """ Stop all services. """
    cmd = 'pkill honcho && docker-compose stop'
    subprocess.call(cmd, shell=True)
