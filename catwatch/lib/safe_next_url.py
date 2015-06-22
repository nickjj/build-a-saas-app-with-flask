from urlparse import urljoin

from flask import request


def safe_next_url(target):
    """
    Ensure a relative URL path is on the same domain as this host.
    This protects against the 'Open redirect vulnerability'.

    :param target: Relative url (typically supplied by Flask-Login)
    :type target: str
    :return: str
    """
    return urljoin(request.host_url, target)
