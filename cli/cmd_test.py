import os
import subprocess

import click

from flask.cli import with_appcontext


@click.command()
@click.argument('path', default=os.path.join('snakeeyes', 'tests'))
@with_appcontext
def test(path):
    """
    Run tests with Pytest.

    :param path: Test path
    :return: Subprocess call result
    """
    cmd = 'py.test {0}'.format(path)
    return subprocess.call(cmd, shell=True)
