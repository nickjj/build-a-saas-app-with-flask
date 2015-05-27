from flask import Blueprint

from catwatch.blueprints.billing.decorators import handle_stripe_exceptions


stripe_webhook = Blueprint('stripe_webhook', __name__,
                           template_folder='../templates',
                           url_prefix='/stripe_webhook')


@stripe_webhook.route('/events')
@handle_stripe_exceptions
def events():
    pass
