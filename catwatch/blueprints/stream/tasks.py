from catwatch.app import create_celery_app

celery = create_celery_app()


@celery.task(rate_limit='10/m')
def broadcast_message(internal_url, data):
    """
    Broadcast the message to anyone listening. We are rate limiting the tweets
    because otherwise it's nearly impossible to read.

    :param internal_url: Full internal websocket URL
    :type internal_url: str
    :param data: Final data to be sent to the websocket server
    :type data: JSON
    :return: None
    """
    # Fix circular import issues.
    from catwatch.blueprints.stream.broadcast import Broadcast

    Broadcast.send_to_websocket_server(internal_url, data)
