import json
import urllib2

from catwatch.blueprints.stream.tasks import broadcast_message


class Broadcast(object):
    @classmethod
    def message(cls, channel, data, internal_url=None, push_token=None):
        """
        Put together a message that will be sent over websockets.

        :param channel: Channel name
        :type channel: str
        :param data: Data to be sent to the websocket server
        :type data: JSON
        :param internal_url: Full internal websocket URL
        :type internal_url: str
        :param push_token: Push token used when broadcasting the message
        :type push_token: str
        :return: dict
        """
        faye_protocol = {
            'channel': channel,
            'data': data,
            'ext': {
                'pushToken': push_token
            }
        }

        broadcast_message.delay(internal_url, faye_protocol)

        return faye_protocol

    @classmethod
    def send_to_websocket_server(cls, internal_url, data):
        """
        Broadcast the message to anyone listening.

        :param internal_url: Full internal websocket URL
        :type internal_url: str
        :param data: Final data to be sent to the websocket server
        :type data: JSON
        :return: urllib2 response object
        """
        request = urllib2.Request(internal_url, data,
                                  {'Content-Type': 'application/json'})

        response = urllib2.urlopen(request, json.dumps(data))

        return response
