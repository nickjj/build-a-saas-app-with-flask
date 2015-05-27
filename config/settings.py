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

# Stripe information.
#
# API keys, NOTE: you should NOT supply them in this config, put them
# in an instance config file, such as: instance/settings.py
#
# They are only listed below to act as documentation since the instance folder
# is not in version control.
STRIPE_SECRET_KEY = None
STRIPE_PUBLISHABLE_KEY = None

# The Stripe API version to use. More information can be found at their docs:
#  https://stripe.com/docs/api/python#versioning
STRIPE_API_VERSION = '2015-04-07'

# Documentation for each plan field below can be found on Stripe's API docs:
#  https://stripe.com/docs/api#create_plan
#
# After supplying both API keys and plans, you must sync the plans by running:
#   run stripe plans
#
# If you are using TEST keys then the plans will be set to livemode: False
# If you are using REAL keys then the plans be set to livemode: True
#
# What the above means is, when you ship your app in production you must sync
# your plans at least once to activate them on your real keys.
STRIPE_PLANS = {
    '0': {
        'id': 'bronze',
        'name': 'Bronze',
        'amount': 100,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'BRONZE MONTHLY'
    },
    '1': {
        'id': 'gold',
        'name': 'Gold',
        'amount': 500,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'GOLD MONTHLY',
        'metadata': {
            'recommended': True
        }
    },
    '2': {
        'id': 'platinum',
        'name': 'Platinum',
        'amount': 1000,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'PLATINUM MONTHLY'
    }
}

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
