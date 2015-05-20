import subprocess

import click

from config import settings
from catwatch.lib.db_seed import seed_database
from catwatch.app import create_app
from catwatch.extensions import db


# Create a context for the database connection.
app = create_app()
db.app = app


def _execute_psql(command):
    """
    Parse a SQLAlchemy database URI.

    :param command: SQL command to run
    :type command: str
    :return: Full docker command to run
    """
    docker = 'docker exec -it website_postgres_1'
    psql = 'psql -U postgres -c "{0}"'.format(command)

    return '{0} {1}'.format(docker, psql)


def _parse_database_uri(uri):
    """
    Parse a SQLAlchemy database URI.

    :return: Dict filled with the URI information
    """
    db_engine = {}

    uri_parts = uri.split('://')
    db_engine['protocol'] = uri_parts[0]

    uri_without_protocol_parts = uri_parts[1].split('@')
    user_and_pass = uri_without_protocol_parts[0].split(':')
    domain_and_db = uri_without_protocol_parts[1].split('/')

    db_engine['username'] = user_and_pass[0]
    db_engine['password'] = user_and_pass[1]
    db_engine['host'] = domain_and_db[0].split(':')[0]
    db_engine['port'] = domain_and_db[0].split(':')[1]
    db_engine['database'] = domain_and_db[1]

    return db_engine


def _create_database_user(user, password, database):
    """
    Execute a database command to create a new user.

    :param user: The user.
    :param password: The password.
    :param password: The database.
    :return: None
    """
    _drop_database_user(database)
    pg = 'CREATE USER {0} WITH PASSWORD \'{1}\';'.format(user, password)

    subprocess.call(_execute_psql(pg), shell=True)


def _grant_user_privileges(user, database):
    """
    Execute a database command to grant all privileges to a user.

    :param user: The database user.
    :param database: The database name.
    :return: None
    """
    pg = 'GRANT ALL PRIVILEGES ON DATABASE {0} to {1};'.format(database, user)

    subprocess.call(_execute_psql(pg), shell=True)


def _drop_database_user(database):
    """
    Execute a database command to drop a user.

    :param database: The database name.
    :return: None
    """
    pg = 'DROP USER IF EXISTS {0};'.format(database)

    subprocess.call(_execute_psql(pg), shell=True)


def _interact_with_database(command, database, if_exists=True):
    """
    Execute a database command to perform a specific action against it.

    :param command: The name of the command to run.
    :param database: The database name.
    :param if_exists: Should we check if it exists or not?
    :return: None
    """
    if if_exists:
        if_exists_flag = '--if-exists'
    else:
        if_exists_flag = ''

    cmd = 'docker exec -it website_postgres_1 {0} -U postgres -e {1} {2}' \
        .format(command, if_exists_flag, database)

    subprocess.call(cmd, shell=True)


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.argument('databases', nargs=-1)
def create(databases):
    """
    Create a user/database.
    """
    db_config = _parse_database_uri(settings.SQLALCHEMY_DATABASE_URI)

    if databases == ():
        databases = [db_config['database']]

    # We only need to create 1 user.
    _create_database_user(db_config['username'], db_config['password'],
                          databases[0])

    for database in databases:
        _interact_with_database('createdb', database, if_exists=False)
        _grant_user_privileges(db_config['username'], database)

    # We also do a create all to load the initial schema from our models.
    db.create_all()


@click.command()
@click.argument('databases', nargs=-1)
def drop(databases):
    """
    Drop a user/database.
    """
    db_config = _parse_database_uri(settings.SQLALCHEMY_DATABASE_URI)

    if databases == ():
        databases = [db_config['database']]

    for database in databases:
        _interact_with_database('dropdb', database)

        # We delete the user last, after every db has been dropped already,
        # otherwise we'll have dependency issues.
        # TODO: Only do this if no DBs exist,
        # drop_database_user(db_config['username'])


@click.command()
@click.argument('databases', nargs=-1)
@click.pass_context
def reset(ctx, databases):
    """
    Run drop, create and seed automatically.
    """
    ctx.invoke(drop, databases=databases)
    ctx.invoke(create, databases=databases)
    ctx.invoke(seed)


@click.command()
def seed():
    """
    Seed the database with your own data.
    """
    seed_database()


cli.add_command(create)
cli.add_command(drop)
cli.add_command(reset)
cli.add_command(seed)
