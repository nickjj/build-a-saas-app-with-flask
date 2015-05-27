from functools import wraps

from flask import redirect, url_for, flash
from flask_babel import gettext as _
import stripe


def handle_stripe_exceptions(f):
    """
    Handle stripe exceptions so they do not throw 500s.

    :param f:
    :type f: Function
    :return: f
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except stripe.error.CardError:
            flash(_('Sorry, your card was declined. Try again perhaps?'),
                  'error')
            return redirect(url_for('user.settings'))
        except stripe.error.InvalidRequestError:
            flash(_('Our payment gateway did not like that request.'), 'error')
            return redirect(url_for('user.settings'))
        except stripe.error.AuthenticationError:
            flash(_('Authentication with our payment gateway failed.'),
                  'error')
            return redirect(url_for('user.settings'))
        except stripe.error.APIConnectionError:
            flash(_(
                'Our payment gateway is experiencing connectivity issues'
                ', please try again.'), 'error')
            return redirect(url_for('user.settings'))
        except stripe.error.StripeError:
            flash(_(
                'Our payment gateway is having issues, please try again.'),
                'error')
            return redirect(url_for('user.settings'))

    return decorated_function

