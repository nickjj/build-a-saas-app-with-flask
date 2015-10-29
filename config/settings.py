# -*- coding: utf-8 -*-

from os import path
from datetime import timedelta

from celery.schedules import crontab


# This value is used for the following properties,
# it really should be your module's name.
#   Database name
#   Cache redis prefix
APP_NAME = 'catwatch'
APP_ROOT = path.join(path.dirname(path.abspath(__file__)), '..')

# App settings, most settings you see here will change in production.
SECRET_KEY = 'pickabettersecret'
DEBUG = True
TESTING = False
LOG_LEVEL = 'DEBUG'

# You will need to disable this to get Stripe's webhooks to work because you'll
# likely end up using tunneling tooling such as ngrok so the endpoints are
# reachable outside of your private network.
#
# The problem with this is, Flask won't allow any connections to the ngrok
# url with the SERVER_NAME set to localhost:8000. However if you comment out
# the SERVER_NAME below then webbooks will work but now url_for will not work
# inside of email templates.
#
# A better solution will turn up in the future.
SERVER_NAME = 'localhost:8000'

# Public build path. Files in this path will be accessible to the internet.
PUBLIC_BUILD_PATH = path.join(APP_ROOT, 'build', 'public')

# Flask-Webpack (assets) settings.
WEBPACK_MANIFEST_PATH = path.join(APP_ROOT, 'build', 'manifest.json')

# Babel i18n translations.
ACCEPT_LANGUAGES = ['en', 'es']
LANGUAGES = {
    'en': 'English',
    'es': u'Español'
}
BABEL_DEFAULT_LOCALE = 'en'

# Seed settings.
SEED_ADMIN_EMAIL = 'dev@localhost.com'

# Database settings,
# The username and password must match what's in docker-compose.yml for dev.
db_uri = 'postgresql://catwatch:bestpassword@localhost:5432/{0}'
SQLALCHEMY_DATABASE_URI = db_uri.format(APP_NAME)
SQLALCHEMY_POOL_SIZE = 5

# Cache settings.
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_KEY_PREFIX = APP_NAME

# Celery settings.
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Celery recurring scheduled tasks.
CELERYBEAT_SCHEDULE = {
    'mark-soon-to-expire-credit-cards': {
        'task': 'catwatch.blueprints.billing.tasks.mark_old_credit_cards',
        'schedule': crontab(hour=12, minute=1)
    },
    'mark-invalid-coupons': {
        'task': 'catwatch.blueprints.billing.tasks.expire_old_coupons',
        'schedule': crontab(hour=12, minute=2)
    },
}

# Login settings.
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Mail settings.
MAIL_DEFAULT_SENDER = 'support@catwatch.com'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'you@gmail.com'
MAIL_PASSWORD = 'awesomepassword'

# External end points.
ENDPOINT_CADVISOR = 'http://localhost:8080/containers/'
ENDPOINT_FLOWER = 'http://localhost:8081'

# Stripe settings.
#
# API keys, NOTE: you should NOT supply them in this config, put them
# in an instance config file, such as: instance/settings.py
#
# They are only listed below to act as documentation.
STRIPE_SECRET_KEY = None
STRIPE_PUBLISHABLE_KEY = None

# The Stripe API version to use. More information can be found on their docs:
#  https://stripe.com/docs/api/python#versioning
STRIPE_API_VERSION = '2015-01-26'

# Documentation for each plan field below can be found on Stripe's API docs:
#  https://stripe.com/docs/api#create_plan
#
# After supplying both API keys and plans, you must sync the plans by running:
#   run stripe sync_plans
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

# Twitter settings.
#
# API keys, NOTE: you should NOT supply them in this config, put them
# in an instance config file, such as: instance/settings.py
#
# They are only listed below to act as documentation.
TWITTER_CONSUMER_KEY = None
TWITTER_CONSUMER_SECRET = None
TWITTER_ACCESS_TOKEN = None
TWITTER_ACCESS_SECRET = None

# Broadcast (websocket server) settings.
#
# NOTE: you should NOT supply the PUSH_TOKEN/BROADCAST_INTERNAL_URL here,
# put them in an instance config file, such as: instance/settings.py
BROADCAST_PUBLIC_URL = 'http://localhost:4242/stream'
BROADCAST_INTERNAL_URL = None
BROADCAST_PUSH_TOKEN = None
