import subprocess

import click

from catwatch.lib.db_seed import seed_database
from catwatch.app import create_app
from catwatch.extensions import db


# Create a context for the database connection.
app = create_app()
db.app = app
SQLALCHEMY_DATABASE_URI = app.config.get('SQLALCHEMY_DATABASE_URI', None)


class PostgresDatabase(object):
    def __init__(self, databases):
        self._config = _parse_database_uri(SQLALCHEMY_DATABASE_URI)
        self._psql = 'psql -U postgres'
        self._createdb = 'createdb -U postgres'
        self._dropdb = 'dropdb -U postgres'

        self._container = _get_postgres_container()
        self._docker_exec = 'docker exec {0}'.format(self._container)

        self.databases = databases

        if databases == ():
            self.databases = [self._config.get('database')]

    @property
    def config(self):
        """
        Return the parsed database URI.

        :return: str
        """
        return self._config

    @property
    def container(self):
        """
        Return the docker container ID of the running postgres instance.

        :return: str
        """
        return self._container

    def psql(self, command):
        """
        Run a psql command and return its results.

        :return: str
        """
        pg = '{0} -c "{1}"'.format(self._psql, command)
        shell_command = '{0} {1}'.format(self._docker_exec, pg)

        return subprocess.call(shell_command, shell=True)

    def _user(self):
        """
        Create a database role (user).

        :return: None
        """
        create_role = "CREATE USER {0} WITH PASSWORD '{1}'".format(
            self.config.get('username'), self.config.get('password'))

        return self.psql(create_role)

    def list(self):
        """
        List all databases.

        :return: psql result
        """
        return self.psql('\l')

    def create(self):
        """
        Create each database.

        :return: None
        """
        self._user()

        for database in self.databases:
            pg = '{0} "{1}"'.format(self._createdb, database)
            command = '{0} {1}'.format(self._docker_exec, pg)

            subprocess.call(command, shell=True)

        return None

    def drop(self):
        """
        Drop each database.

        :return: None
        """
        for database in self.databases:
            pg = '{0} "{1}"'.format(self._dropdb, database)
            command = '{0} {1}'.format(self._docker_exec, pg)

            subprocess.call(command, shell=True)

        return None


def _parse_database_uri(uri):
    """
    Parse a SQLAlchemy database URI.

    :param uri: Postgres URI
    :type uri: str
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


def _get_postgres_container():
    """
    Find the name of the postgres container.

    :return: str
    """
    find_container = '''
        for i in $(docker ps  | grep "postgres" | cut -f1 -d" ");
          do echo $i;
        done
    '''
    container_id = subprocess.check_output(find_container, shell=True)[:-1]

    return container_id


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
def list():
    """
    List all databases.

    :return: psql result
    """
    database = PostgresDatabase(())
    database.list()


@click.command()
@click.argument('command')
def psql(command):
    """
    Exec a psql command against the database.

    Example, to list all users:
      run db psql "\du"

    Delete a specific user:
      run db psql "DROP USER foobar"

    :return: psql result
    """
    database = PostgresDatabase(())
    database.psql(command)


@click.command()
@click.argument('databases', nargs=-1)
def create(databases):
    """
    Create 1 or more databases.

    :return: db session create_all result
    """
    database = PostgresDatabase(databases)
    database.create()

    # We also do a create all to load the initial schema from our models.
    return db.create_all()


@click.command()
@click.argument('databases', nargs=-1)
def drop(databases):
    """
    Drop 1 or more databases.

    :return: None
    """
    database = PostgresDatabase(databases)
    database.drop()

    return None


@click.command()
@click.argument('databases', nargs=-1)
@click.pass_context
def reset(ctx, databases):
    """
    Run drop, create and seed automatically.

    :return: None
    """
    ctx.invoke(drop, databases=databases)
    ctx.invoke(create, databases=databases)
    ctx.invoke(seed)

    return None


@click.command()
def init():
    """
    Initialize the database.

    :return: db session create_all result
    """
    db.drop_all()
    return db.create_all()


@click.command()
def seed():
    """
    Seed the database with your own data.
    """
    return seed_database()


cli.add_command(list)
cli.add_command(psql)
cli.add_command(create)
cli.add_command(drop)
cli.add_command(reset)
cli.add_command(init)
cli.add_command(seed)
