import logging

import click

from catwatch.app import create_app
from catwatch.blueprints.stream.twitter import TwitterStream

app = create_app()

# Configuration.
TWITTER_CONSUMER_KEY = app.config.get('TWITTER_CONSUMER_KEY', None)
TWITTER_CONSUMER_SECRET = app.config.get('TWITTER_CONSUMER_SECRET', None)
TWITTER_ACCESS_TOKEN = app.config.get('TWITTER_ACCESS_TOKEN', None)
TWITTER_ACCESS_SECRET = app.config.get('TWITTER_ACCESS_SECRET', None)

BROADCAST_URL = app.config.get('BROADCAST_URL', None)
BROADCAST_AUTH_TOKEN = app.config.get('BROADCAST_AUTH_TOKEN', None)


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
    if BROADCAST_URL is None or BROADCAST_AUTH_TOKEN is None:
        logging.error('Unable to broadcast, missing BROADCAST_HOST and/or '
                      'BROADCAST_AUTH_TOKEN')
        exit(1)

    twitter_stream = TwitterStream(consumer_key=TWITTER_CONSUMER_KEY,
                                   consumer_secret=TWITTER_CONSUMER_SECRET,
                                   access_token=TWITTER_ACCESS_TOKEN,
                                   access_secret=TWITTER_ACCESS_SECRET,
                                   broadcast=True,
                                   broadcast_url=BROADCAST_URL,
                                   broadcast_auth_token=BROADCAST_AUTH_TOKEN)
    twitter_stream.listen()


cli.add_command(listen)
cli.add_command(broadcast)
