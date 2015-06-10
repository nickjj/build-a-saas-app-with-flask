import logging

import click
import stripe

from catwatch.blueprints.billing.services import StripePlan


STRIPE_SECRET_KEY = None
STRIPE_PLANS = None

try:
    from instance import settings
    STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
    STRIPE_PLANS = settings.STRIPE_PLANS
except ImportError:
    logging.error('Your instance/ folder must contain an __init__.py file')
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
        plan = StripePlan.retrieve(value['id'])
        if plan:
            StripePlan.update(value)
        else:
            StripePlan.create(value)

    return None


@click.command()
@click.argument('plan_ids', nargs=-1)
def delete_plans(plan_ids):
    """
    Delete 1 or more plans from Stripe.

    :return: None
    """
    for plan_id in plan_ids:
        StripePlan.delete(plan_id)

    return None


@click.command()
def list_plans():
    """
    List all existing plans on Stripe.

    :return: Stripe plan list
    """
    return logging.info(StripePlan.list())


cli.add_command(sync_plans)
cli.add_command(delete_plans)
cli.add_command(list_plans)
