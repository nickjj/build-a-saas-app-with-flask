from flask import Blueprint, request
from stripe.error import InvalidRequestError

from catwatch.lib.util_json import render_json
from catwatch.extensions import csrf
from catwatch.blueprints.billing.models.invoice import Invoice
from catwatch.blueprints.billing.gateways.stripecom import \
    Event as PaymentEvent

stripe_webhook = Blueprint('stripe_webhook', __name__,
                           url_prefix='/stripe_webhook')


@stripe_webhook.route('/event', methods=['POST'])
@csrf.exempt
def event():
    if not request.json:
        return render_json(406, {'error': 'Mime-type is not application/json'})

    if request.json.get('id') is None:
        return render_json(406, {'error': 'Invalid Stripe event'})

    try:
        safe_event = PaymentEvent.retrieve(request.json.get('id'))
        parsed_event = Invoice.parse_from_event(safe_event)

        Invoice.prepare_and_save(parsed_event)
    except InvalidRequestError as e:
        # We could not parse the event.
        return render_json(422, {'error': str(e)})
    except Exception as e:
        # Return a 200 because something is really wrong and we want Stripe to
        # stop trying to fulfill this webhook request.
        return render_json(200, {'error': str(e)})

    return render_json(200, {'success': True})
