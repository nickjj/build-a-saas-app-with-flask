import pytest

from catwatch.app import create_app
from catwatch.extensions import db as _db
from catwatch.blueprints.user.models import User


@pytest.yield_fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    _app = create_app()

    _app.config['DEBUG'] = False
    _app.config['TESTING'] = True
    _app.config['WTF_CSRF_ENABLED'] = False

    # We want to use a test database rather than our development database.
    db_uri = _app.config['SQLALCHEMY_DATABASE_URI']
    _app.config['SQLALCHEMY_DATABASE_URI'] = '{0}_test'.format(db_uri)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Setup our database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    # Insert a few user accounts.
    admin = User(role='admin', email='admin@localhost.com',
                 password='password')
    disabled = User(active=False, email='disabled@localhost.com',
                    password='password')

    _db.session.add(admin)
    _db.session.add(disabled)
    _db.session.commit()

    return _db


@pytest.yield_fixture(scope='function')
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and postgres does.

    Read more about this at:
    http://stackoverflow.com/a/26624146

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope='session')
def token(db):
    """
    Serialize a JWS token.

    :param db: Pytest fixture
    :return: JWS token
    """
    user = User.find_by_identity('admin@localhost.com')
    return user.serialize_token()
