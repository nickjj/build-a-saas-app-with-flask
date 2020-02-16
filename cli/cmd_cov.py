import subprocess

import click

from flask.cli import with_appcontext


@click.command()
@click.argument('path', default='snakeeyes')
@with_appcontext
def cov(path):
    """
    Run a test coverage report.

    :param path: Test coverage path
    :return: Subprocess call result
    """
    cmd = 'py.test --cov-report term-missing --cov {0}'.format(path)
    return subprocess.call(cmd, shell=True)
