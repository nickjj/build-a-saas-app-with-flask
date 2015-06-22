import json
import logging

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream

from catwatch.blueprints.stream.broadcast import Broadcast


class CatStream(StreamListener):
    def __init__(self, broadcast=False, broadcast_internal_url=None,
                 broadcast_push_token=None):
        super(CatStream, self).__init__()

        self.broadcast = broadcast
        self.broadcast_internal_url = broadcast_internal_url
        self.broadcast_push_token = broadcast_push_token

    def on_data(self, data):
        """
        When data comes in, parse and broadcast the information we care about.

        :param data: JSON returned by Twitter's API.
        :type data: JSON
        :return: bool
        """
        data = json.loads(data)

        params = {
            'created_at': data.get('created_at'),
            'user': data.get('user').get('screen_name'),
            'tweet': data.get('text'),
            'type': self._parse_type(data)
        }

        logging.info(params)

        if self.broadcast:
            Broadcast.message('/cats', params,
                              internal_url=self.broadcast_internal_url,
                              push_token=self.broadcast_push_token)

        return True

    def on_error(self, status_code):
        """
        Catch specific errors thrown by Twitter's API.

        Error codes can be found here:
          https://dev.twitter.com/overview/api/response-codes

        :param status_code: Response code returned by Twitter
        :return: bool
        """
        logging.error('Twitter API error #{0} occurred'.format(status_code))

        return True

    def _parse_type(self, tweet):
        """
        Determine if we're dealing with a tweet, RT or favorite.

        :param tweet: Twitter API response for a Tweet
        :return: Tweet status
        """
        status = None
        if tweet.get('favorited'):
            status = 'favorite'
        elif tweet.get('text').startswith('RT @'):
            status = 'retweet'
        else:
            status = 'tweet'

        return status


class TwitterStream(object):
    def __init__(self, consumer_key=None, consumer_secret=None,
                 access_token=None, access_secret=None,
                 broadcast_internal_url=None, broadcast_push_token=None,
                 broadcast=False):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        self.auth = auth
        self.stream = CatStream(broadcast=broadcast,
                                broadcast_internal_url=broadcast_internal_url,
                                broadcast_push_token=broadcast_push_token)

    def listen(self):
        """
        Authenticate to Twitter and listen on the CatStream.

        :return: None
        """
        stream = Stream(self.auth, self.stream)
        stream.filter(track=['cats'])
