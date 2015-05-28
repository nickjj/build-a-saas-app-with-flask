from flask import jsonify


def render_json(status, *args, **kwargs):
    """
    Return a JSON response.

    :param status: HTTP status code
    :type status: int
    :param args:
    :param kwargs:
    :return: Flask response
    """
    response = jsonify(*args, **kwargs)
    response.status_code = status

    return response
