import subprocess

import click


@click.command()
def cli():
    """
    Stop all services.

    :return: Subprocess call result
    """
    cmd = 'pkill honcho && docker-compose stop'
    return subprocess.call(cmd, shell=True)
