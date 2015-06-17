import click
from alembic import command
from alembic.config import Config

from catwatch.app import create_app
from catwatch.extensions import db


# Create a context for the database connection.
app = create_app()
db.app = app


def _get_config():
    """
    Return an alembic config.

    :return: config
    """
    config = Config('alembic.ini')
    config.set_main_option('script_location', 'migrations')
    return config


@click.group()
def cli():
    """ Run alembic related tasks. """
    pass


@click.command()
def init():
    """ Initialize a new database migration. """
    config = _get_config()
    return command.init(config, 'migrations', 'alembic')


@click.command()
def current():
    """ Display revisions for each database. """
    config = _get_config()
    return command.current(config)


@click.command()
@click.option('--rev-range', default=None,
              help='Specify a revision range, formatted as [start]:[end]')
def history(rev_range=None):
    """ List changes in chronological order. """
    config = _get_config()
    return command.history(config, rev_range)


@click.command()
@click.option('--sql', default=False,
              help='Emit revision to SQL, if False it will write to STDOUT.')
@click.option('--autogenerate', default=False,
              help='Preset revision file based on comparing the db to model.')
@click.option('-m', '--message', default=None)
def revision(message=None, autogenerate=False, sql=False):
    """ Create a new revision file. """
    config = _get_config()
    return command.revision(config, message, autogenerate=autogenerate,
                            sql=sql)


@click.command()
@click.option('--sql', default=False,
              help='Emit revision to SQL, if False it will write to STDOUT.')
@click.option('-m', '--message', default=None)
def auto(message=None, sql=False):
    """ Alias for 'revision --autogenerate'. """
    config = _get_config()
    return command.revision(config, message, autogenerate=True, sql=sql)


@click.command()
@click.option('--tag', default=None,
              help='Arbitrary tag name, may be used by custom env.py scripts.')
@click.option('--sql', default=False,
              help='Emit revision to SQL, if False it will write to STDOUT.')
@click.option('--revision', help='Revision identifier.')
def stamp(revision='head', sql=False, tag=None):
    """ Stamp the revision table but don't migrate."""
    config = _get_config()
    return command.stamp(config, revision, sql=sql, tag=tag)


@click.command()
@click.option('--tag', default=None,
              help='Arbitrary tag name, may be used by custom env.py scripts.')
@click.option('--sql', default=False,
              help='Emit revision to SQL, if False it will write to STDOUT.')
@click.option('--revision', default='head', help='Revision identifier.')
def upgrade(revision='head', sql=False, tag=None):
    """ Update to a later revision. """
    config = _get_config()
    return command.upgrade(config, revision, sql=sql, tag=tag)


@click.command()
@click.option('--tag', default=None,
              help='Arbitrary tag name, may be used by custom env.py scripts.')
@click.option('--sql', default=False,
              help='Emit revision to SQL, if False it will write to STDOUT.')
@click.option('--revision', nargs='?', default='-1',
              help='Revision identifier.')
def downgrade(revision='-1', sql=False, tag=None):
    """ Revert to a previous revision. """
    config = _get_config()
    return command.downgrade(config, revision, sql=sql, tag=tag)


@click.command()
def branches():
    """
    List revision history.
    """
    config = _get_config()
    return command.branches(config)


cli.add_command(init)
cli.add_command(current)
cli.add_command(history)
cli.add_command(revision)
cli.add_command(auto)
cli.add_command(stamp)
cli.add_command(upgrade)
cli.add_command(downgrade)
cli.add_command(branches)
