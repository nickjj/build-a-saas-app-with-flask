from functools import wraps

from flask import flash, redirect
from flask_babel import gettext as _
from flask_login import current_user


def anonymous_required(url='/settings'):
    """
    Redirect a user to a specified location if they are already signed in.

    :param url: URL to be redirected to if invalid
    :type url: str
    :return: Function
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated():
                return redirect(url)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def role_required(*roles):
    """
    Does a user have permission to view this page?

    :param *roles: 1 or more allowed roles
    :return: Function
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash(_('You do not have permission to do that.'), 'error')
                return redirect('/')

            return f(*args, **kwargs)

        return decorated_function

    return decorator
