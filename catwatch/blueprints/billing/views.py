from flask import Blueprint, current_app, render_template, url_for, request, \
    redirect, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _

from config import settings
from catwatch.blueprints.billing.forms import CreditCardForm, \
    CancelSubscriptionForm
from catwatch.blueprints.billing.models import Subscription, CreditCard


billing = Blueprint('billing', __name__, template_folder='templates',
                    url_prefix='/subscription')


@billing.route('/pricing')
def pricing():
    if current_user.subscription:
        return redirect(url_for('billing.update'))

    return render_template('billing/pricing.jinja2',
                           plans=settings.STRIPE_PLANS)


@billing.route('/create', methods=['GET', 'POST'])
@login_required
def create():
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
        if subscription.create():
            flash(_('Awesome, thanks for subscribing!'), 'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/payment_method.jinja2',
                           form=form, plan=active_plan)


@billing.route('/update')
@login_required
def update():
    if not current_user.subscription:
        return redirect(url_for('billing.pricing'))

    current_plan = current_user.subscription.plan
    active_plan = Subscription.get_plan_by_stripe_id(current_plan)

    new_plan = request.args.get('plan', None)
    plan = Subscription.get_plan_by_stripe_id(new_plan)

    # Guard against an invalid, missing or identical plan.
    is_same_plan = new_plan == active_plan['id']
    if (new_plan is not None and plan is None) or is_same_plan:
        return redirect(url_for('billing.update'))

    if new_plan:
        params = {
            'user': current_user,
            'plan': plan['id']
        }

        subscription = Subscription(**params)
        if subscription.update():
            flash(_('Your subscription has been updated.'), 'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/pricing.jinja2',
                           plans=settings.STRIPE_PLANS,
                           active_plan=active_plan)


@billing.route('/cancel', methods=['GET', 'POST'])
@login_required
def cancel():
    if not current_user.subscription:
        flash(_('You do not have an active subscription.'), 'error')
        return redirect(url_for('user.settings'))

    form = CancelSubscriptionForm()

    if form.validate_on_submit():
        params = {'user': current_user}

        subscription = Subscription(**params)
        if subscription.cancel():
            flash(_(
                'Sorry to see you go, your subscription has been cancelled.'),
                'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/cancel.jinja2',
                           form=form)


@billing.route('/update_payment_method', methods=['GET', 'POST'])
@login_required
def update_payment_method():
    if not current_user.credit_card:
        flash(_('You do not have a payment method on file.'), 'error')
        return redirect(url_for('user.settings'))

    active_plan = Subscription.get_plan_by_stripe_id(
        current_user.subscription.plan)

    card_last4 = str(current_user.credit_card.last4)
    stripe_key = current_app.config['STRIPE_PUBLISHABLE_KEY']
    form = CreditCardForm(stripe_key=stripe_key,
                          plan=active_plan,
                          name=current_user.name)

    if form.validate_on_submit():
        params = {
            'user': current_user,
            'name': request.form.get('name', None),
            'stripe_token': request.form.get('stripe_token', None)
        }

        subscription = Subscription(**params)
        if subscription.update_payment_method():
            flash(_('Your payment method has been updated.'), 'success')
            return redirect(url_for('user.settings'))

    return render_template('billing/payment_method.jinja2', form=form,
                           plan=active_plan, card_last4=card_last4)
