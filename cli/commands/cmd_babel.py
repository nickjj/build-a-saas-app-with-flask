import subprocess

import click

from config import settings


MESSAGES_PATH = settings.APP_ROOT + '/catwatch/i18n/messages.pot'
TRANSLATION_PATH = settings.APP_ROOT + '/catwatch/i18n/translations'


@click.group()
def cli():
    """ Manage i18n translations. """
    pass


@click.command()
def extract():
    """
    Extract strings into a pot file.
    """
    babel_cmd = 'pybabel extract -F babel.cfg -k lazy_gettext ' \
                '-o {0} catwatch'.format(MESSAGES_PATH)
    subprocess.call(babel_cmd, shell=True)


@click.option('--language', default=None, help='The output language, ex. de')
@click.command()
def init(language=None):
    """
    Map translations to a different language.
    """
    babel_cmd = 'pybabel init -i {0} -d {1} -l {2}'.format(MESSAGES_PATH,
                                                           TRANSLATION_PATH,
                                                           language)
    subprocess.call(babel_cmd, shell=True)


@click.command()
def compile():
    """
    Compile new translations.
    """
    babel_cmd = 'pybabel compile -d {0}'.format(TRANSLATION_PATH)
    subprocess.call(babel_cmd, shell=True)


@click.command()
def update():
    """
    Update existing translations.
    """
    babel_cmd = 'pybabel update -i {0} -d {1}'.format(MESSAGES_PATH,
                                                      TRANSLATION_PATH)
    subprocess.call(babel_cmd, shell=True)


cli.add_command(extract)
cli.add_command(init)
cli.add_command(compile)
cli.add_command(update)
