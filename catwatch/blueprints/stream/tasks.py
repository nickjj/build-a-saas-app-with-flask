from catwatch.app import create_celery_app

celery = create_celery_app()


@celery.task()
def broadcast_message(url, data):
    """
    Broadcast the message to anyone listening.

    :param url: Full websocket URL
    :type url: str
    :param data: Final data to be sent to the websocket server
    :type data: JSON
    :return: None
    """
    # Fix circular import issues.
    from catwatch.blueprints.stream.broadcast import Broadcast
    Broadcast.send_to_websocket_server(url, data)
