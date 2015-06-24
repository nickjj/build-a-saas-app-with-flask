import logging

import click
import stripe

from catwatch.blueprints.billing.gateways.stripecom import Plan as PaymentPlan

STRIPE_SECRET_KEY = None
STRIPE_PLANS = None

try:
    from instance import settings

    STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
    STRIPE_PLANS = settings.STRIPE_PLANS
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    if STRIPE_SECRET_KEY is None:
        STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
    if STRIPE_PLANS is None:
        STRIPE_PLANS = settings.STRIPE_PLANS


@click.group()
def cli():
    """ Perform various tasks with Stripe's API. """
    stripe.api_key = STRIPE_SECRET_KEY


@click.command()
def sync_plans():
    """
    Sync (upsert) STRIPE_PLANS to Stripe.

    :return: None
    """
    if STRIPE_PLANS is None:
        return None

    for _, value in STRIPE_PLANS.iteritems():
        plan = PaymentPlan.retrieve(value.get('id'))
        if plan:
            PaymentPlan.update(id=value.get('id'),
                               name=value.get('name'),
                               metadata=value.get('metadata'),
                               statement_descriptor=value.get(
                                   'statement_descriptor'))
        else:
            PaymentPlan.create(**value)

    return None


@click.command()
@click.argument('plan_ids', nargs=-1)
def delete_plans(plan_ids):
    """
    Delete 1 or more plans from Stripe.

    :return: None
    """
    for plan_id in plan_ids:
        PaymentPlan.delete(plan_id)

    return None


@click.command()
def list_plans():
    """
    List all existing plans on Stripe.

    :return: Stripe plans
    """
    return logging.info(PaymentPlan.list())


cli.add_command(sync_plans)
cli.add_command(delete_plans)
cli.add_command(list_plans)
