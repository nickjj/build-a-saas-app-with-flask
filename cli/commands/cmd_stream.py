import logging

import click

try:
    from instance import settings
except ImportError:
    logging.error('Your instance/ folder must contain an __init__.py file')
    exit(1)

from catwatch.app import create_app
from catwatch.blueprints.stream.twitter import TwitterStream

app = create_app()

# Configuration.
TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_SECRET = settings.TWITTER_ACCESS_SECRET

BROADCAST_INTERNAL_URL = settings.BROADCAST_INTERNAL_URL
BROADCAST_PUSH_TOKEN = settings.BROADCAST_PUSH_TOKEN


@click.group()
def cli():
    """ Listen or broadcast the Twitter stream. """
    pass


@click.command()
def listen():
    """
    Listen on the Twitter stream.
    """
    twitter_stream = TwitterStream(consumer_key=TWITTER_CONSUMER_KEY,
                                   consumer_secret=TWITTER_CONSUMER_SECRET,
                                   access_token=TWITTER_ACCESS_TOKEN,
                                   access_secret=TWITTER_ACCESS_SECRET)
    twitter_stream.listen()


@click.command()
def broadcast():
    """
    Listen on and broadcast the Twitter stream.
    """
    if BROADCAST_INTERNAL_URL is None or BROADCAST_PUSH_TOKEN is None:
        logging.error('Unable to broadcast, missing BROADCAST_INTERNAL_URL '
                      'and/or BROADCAST_PUSH_TOKEN')
        exit(1)

    twitter_stream = TwitterStream(consumer_key=TWITTER_CONSUMER_KEY,
                                   consumer_secret=TWITTER_CONSUMER_SECRET,
                                   access_token=TWITTER_ACCESS_TOKEN,
                                   access_secret=TWITTER_ACCESS_SECRET,
                                   broadcast=True,
                                   broadcast_internal_url=BROADCAST_INTERNAL_URL,
                                   broadcast_push_token=BROADCAST_PUSH_TOKEN)
    twitter_stream.listen()


cli.add_command(listen)
cli.add_command(broadcast)
