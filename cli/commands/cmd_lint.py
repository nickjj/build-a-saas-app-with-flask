import subprocess

import click

from config import settings


PACKAGE_PATH = settings.APP_ROOT + '/catwatch'


@click.command()
@click.argument('path', default=PACKAGE_PATH)
def cli(path):
    """ Run flake8 to analyze the codebase. """
    cmd = 'flake8 {0}'.format(path)
    subprocess.call(cmd, shell=True)
