from flask import Blueprint, current_app, render_template, url_for, request, \
    redirect, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _

from config import settings
from catwatch.blueprints.billing.forms import CreditCardForm
from catwatch.blueprints.billing.models import Subscription


billing = Blueprint('billing', __name__, template_folder='templates',
                    url_prefix='/payment')


@billing.route('/pricing')
def pricing():
    return render_template('billing/pricing.jinja2',
                           plans=settings.STRIPE_PLANS)


@billing.route('/process', methods=['GET', 'POST'])
@login_required
def process():
    if current_user.subscription:
        flash(_('You already have an active subscription.'), 'info')
        return redirect(url_for('user.settings'))

    plan = request.args.get('plan', None)
    active_plan = Subscription.get_plan_by_stripe_id(plan)

    # Guard against an invalid or missing plan.
    if active_plan is None and request.method == 'GET':
        return redirect(url_for('billing.pricing'))

    stripe_key = current_app.config['STRIPE_PUBLISHABLE_KEY']
    form = CreditCardForm(stripe_key=stripe_key, plan=plan)

    if form.validate_on_submit():
        params = {
            'user': current_user,
            'name': request.form.get('name', None),
            'plan': request.form.get('plan', None),
            'stripe_token': request.form.get('stripe_token', None)
        }

        subscription = Subscription(**params)
        if subscription.begin_membership():
            flash(_('Awesome, thanks for subscribing!'), 'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/process.jinja2',
                           form=form, plan=active_plan)
