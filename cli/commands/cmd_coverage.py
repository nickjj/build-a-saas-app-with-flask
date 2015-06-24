import logging
import subprocess

import click

try:
    from instance import settings

    APP_ROOT = settings.APP_ROOT
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    APP_ROOT = settings.APP_ROOT

PACKAGE_PATH = '{0}/{1}'.format(APP_ROOT, '/catwatch')


@click.command()
@click.argument('path', default=PACKAGE_PATH)
def cli(path):
    """
    Run test coverage report.

    :return: Subprocess call result
    """
    cmd = 'py.test --cov-report term-missing --cov {0} {0}'.format(path)
    return subprocess.call(cmd, shell=True)
