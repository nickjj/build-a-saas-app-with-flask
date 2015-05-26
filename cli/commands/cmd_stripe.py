import click
import stripe

from config import settings
from catwatch.blueprints.billing.services import StripePlan

from catwatch.app import create_app

app = create_app()


@click.group()
def cli():
    """ Perform various tasks with Stripe's API. """
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY', None)


@click.command()
def sync_plans():
    """
    Sync (upsert) STRIPE_PLANS to Stripe.
    """

    plans = settings.STRIPE_PLANS

    for _, value in plans.iteritems():
        plan = StripePlan.retrieve(value['id'])
        if plan:
            StripePlan.update(value)
        else:
            StripePlan.create(value)


@click.command()
@click.argument('plan_ids', nargs=-1)
def delete_plans(plan_ids):
    """
    Delete 1 or more plans from Stripe.
    """
    for plan_id in plan_ids:
        StripePlan.delete(plan_id)


@click.command()
def list_plans():
    """
    List all existing plans on Stripe.
    """
    print(StripePlan.list())


cli.add_command(sync_plans)
cli.add_command(delete_plans)
cli.add_command(list_plans)
