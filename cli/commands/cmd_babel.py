import logging
import subprocess

import click

APP_ROOT = None
APP_NAME = None

try:
    from instance import settings

    APP_ROOT = settings.APP_ROOT
    APP_NAME = settings.APP_NAME
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    if APP_ROOT is None:
        APP_ROOT = settings.APP_ROOT

    if APP_NAME is None:
        APP_NAME = settings.APP_NAME

BABEL_I18N_PATH = '{0}/{1}'.format(APP_NAME, 'translations')
MESSAGES_PATH = '{0}/{1}/{2}'.format(APP_ROOT, BABEL_I18N_PATH, 'messages.pot')
TRANSLATION_PATH = '{0}/{1}'.format(APP_ROOT, BABEL_I18N_PATH)


@click.group()
def cli():
    """ Manage i18n translations. """
    pass


@click.command()
def extract():
    """
    Extract strings into a pot file.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel extract -F babel.cfg -k lazy_gettext ' \
                '-o {0} catwatch'.format(MESSAGES_PATH)
    return subprocess.call(babel_cmd, shell=True)


@click.option('--language', default=None, help='The output language, ex. de')
@click.command()
def init(language=None):
    """
    Map translations to a different language.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel init -i {0} -d {1} -l {2}'.format(MESSAGES_PATH,
                                                           TRANSLATION_PATH,
                                                           language)
    return subprocess.call(babel_cmd, shell=True)


@click.command()
def compile():
    """
    Compile new translations. Remember to remove #, fuzzy lines.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel compile -d {0}'.format(TRANSLATION_PATH)
    return subprocess.call(babel_cmd, shell=True)


@click.command()
def update():
    """
    Update existing translations.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel update -i {0} -d {1}'.format(MESSAGES_PATH,
                                                      TRANSLATION_PATH)
    return subprocess.call(babel_cmd, shell=True)


cli.add_command(extract)
cli.add_command(init)
cli.add_command(compile)
cli.add_command(update)
