import datetime
import logging
import random
from time import sleep

import click
import pytz

from faker import Faker

from catwatch.blueprints.stream.twitter import TwitterStream
from catwatch.blueprints.stream.tasks import broadcast_message

TWITTER_CONSUMER_KEY = None
TWITTER_CONSUMER_SECRET = None
TWITTER_ACCESS_TOKEN = None
TWITTER_ACCESS_SECRET = None

BROADCAST_PUSH_TOKEN = None
BROADCAST_INTERNAL_URL = None

try:
    from instance import settings

    TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
    TWITTER_CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
    TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_SECRET = settings.TWITTER_ACCESS_SECRET

    BROADCAST_PUSH_TOKEN = settings.BROADCAST_PUSH_TOKEN
    BROADCAST_INTERNAL_URL = settings.BROADCAST_INTERNAL_URL
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    if TWITTER_CONSUMER_KEY is None:
        TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY

    if TWITTER_CONSUMER_SECRET is None:
        TWITTER_CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET

    if TWITTER_ACCESS_TOKEN is None:
        TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN

    if TWITTER_ACCESS_SECRET is None:
        TWITTER_ACCESS_SECRET = settings.TWITTER_ACCESS_SECRET

    if BROADCAST_PUSH_TOKEN is None:
        BROADCAST_PUSH_TOKEN = settings.BROADCAST_PUSH_TOKEN

    if BROADCAST_INTERNAL_URL is None:
        BROADCAST_INTERNAL_URL = settings.BROADCAST_INTERNAL_URL


@click.group()
def cli():
    """ Listen or broadcast the Twitter stream. """
    pass


@click.command()
def listen():
    """
    Listen on the Twitter stream.

    :return: Twitter stream
    """
    if None in ('TWITTER_CONSUMER_KEY',
                TWITTER_CONSUMER_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET):
        logging.error('Unable to broadcast, missing twitter settings')
        exit(1)

    stream = TwitterStream(consumer_key=TWITTER_CONSUMER_KEY,
                           consumer_secret=TWITTER_CONSUMER_SECRET,
                           access_token=TWITTER_ACCESS_TOKEN,
                           access_secret=TWITTER_ACCESS_SECRET)

    return stream.listen()


@click.command()
def broadcast():
    """
    Listen on and broadcast the Twitter stream.

    :return: Twitter stream
    """
    if None in ('TWITTER_CONSUMER_KEY',
                TWITTER_CONSUMER_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET):
        logging.error('Unable to broadcast, missing twitter settings')
        exit(1)

    if BROADCAST_INTERNAL_URL is None or BROADCAST_PUSH_TOKEN is None:
        logging.error('Unable to broadcast, missing broadcast settings')
        exit(1)

    stream = TwitterStream(consumer_key=TWITTER_CONSUMER_KEY,
                           consumer_secret=TWITTER_CONSUMER_SECRET,
                           access_token=TWITTER_ACCESS_TOKEN,
                           access_secret=TWITTER_ACCESS_SECRET,
                           broadcast=True,
                           broadcast_internal_url=BROADCAST_INTERNAL_URL,
                           broadcast_push_token=BROADCAST_PUSH_TOKEN)

    return stream.listen()


@click.command()
def fake_broadcast():
    """
    Broadcast fake events (useful for testing).

    :return: None
    """
    fake = Faker()

    while True:
        random_types = ('tweet', 'retweet', 'favorite')
        random_tweet = fake.text(max_nb_chars=140)

        data = {
            'created_at': str(datetime.datetime.now(pytz.utc)),
            'type': random.choice(random_types),
            'tweet': random_tweet,
            'user': fake.user_name()
        }

        faye_protocol = {
            'channel': '/cats',
            'data': data,
            'ext': {
                'pushToken': BROADCAST_PUSH_TOKEN
            }
        }

        broadcast_message.delay(BROADCAST_INTERNAL_URL, faye_protocol)
        logging.info(data)
        sleep(1)

    return None


cli.add_command(listen)
cli.add_command(broadcast)
cli.add_command(fake_broadcast)
