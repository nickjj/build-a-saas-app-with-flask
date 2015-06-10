import logging
import subprocess

import click

try:
    from instance import settings
    APP_ROOT = settings.APP_ROOT
except ImportError:
    logging.error('Your instance/ folder must contain an __init__.py file')
    exit(1)
except AttributeError:
    from config import settings
    APP_ROOT = settings.APP_ROOT


TESTS_PATH = '{0}/{1}'.format(APP_ROOT, '/catwatch/tests')


@click.command()
@click.argument('path', default=TESTS_PATH)
def cli(path):
    """
    Run tests.

    :return: Subprocess call result
    """
    cmd = 'py.test {0}'.format(path)
    return subprocess.call(cmd, shell=True)
