import subprocess

import click

from config import settings


TESTS_PATH = settings.APP_ROOT + '/catwatch/tests'


@click.command()
@click.argument('path', default=TESTS_PATH)
def cli(path):
    """ Run tests. """
    cmd = 'py.test {0}'.format(path)
    subprocess.call(cmd, shell=True)
