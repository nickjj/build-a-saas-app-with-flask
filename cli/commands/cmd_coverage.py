import subprocess

import click

from config import settings


PACKAGE_PATH = settings.APP_ROOT + '/catwatch'


@click.command()
@click.argument('path', default=PACKAGE_PATH)
def cli(path):
    """ Run test coverage report. """
    cmd = 'py.test --cov-report term-missing --cov {0} {0}'.format(path)
    subprocess.call(cmd, shell=True)
