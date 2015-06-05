import json
import urllib2

from catwatch.blueprints.stream.tasks import broadcast_message


class Broadcast(object):
    @classmethod
    def message(cls, channel, data, url=None, auth_token=None):
        """
        Put together a message that will be sent over websockets.

        :param channel: Channel name
        :type channel: str
        :param data: Data to be sent to the websocket server
        :type data: JSON
        :param url: Full websocket URL
        :type url: str
        :param auth_token: Auth token used when broadcasting the message
        :type auth_token: str
        :return: Dict of what's being sent
        """
        faye_protocol = {
            'channel': channel,
            'data': data,
            'ext': {
                'pushToken': auth_token
            }
        }

        broadcast_message.delay(url, faye_protocol)

        return faye_protocol

    @classmethod
    def send_to_websocket_server(cls, url, data):
        """
        Broadcast the message to anyone listening.

        :param url: Full websocket URL
        :type url: str
        :param data: Final data to be sent to the websocket server
        :type data: JSON
        :return: urllib2 response object
        """
        request = urllib2.Request(url, data,
                                  {'Content-Type': 'application/json'})

        response = urllib2.urlopen(request, json.dumps(data))

        return response
