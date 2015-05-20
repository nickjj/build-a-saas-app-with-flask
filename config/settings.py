from os import path
from datetime import timedelta


# This should be the name of the database you want to create
APP_NAME = 'catwatch'

# App settings.
APP_ROOT = path.join(path.dirname(path.abspath(__file__)), '..')
SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'pickabettersecret'
DEBUG = True
TESTING = False
LOG_LEVEL = 'info'

# Assets.
WEBPACK_STATS_PATH = APP_ROOT + '/build/manifest.json'

# Babel i18n translations.
ACCEPT_LANGUAGES = ['en']
LANGUAGES = {
    'en': u'English'
}

# Database.
# The username and password must match what's in docker-compose.yml.
db_uri = 'postgresql://catwatch:bestpassword@localhost:5432/{0}'
SQLALCHEMY_DATABASE_URI = db_uri.format(APP_NAME)
SQLALCHEMY_POOL_SIZE = 5

# Cache.
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_KEY_PREFIX = APP_NAME

# Celery background worker.
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_REDIS_MAX_CONNECTIONS = 5

# Login.
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Mail.
MAIL_DEFAULT_SENDER = 'support@catwatch.com'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'you@gmail.com'
MAIL_PASSWORD = 'awesomepassword'
