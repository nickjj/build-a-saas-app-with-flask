from datetime import datetime
import random

import click
from faker import Faker

from catwatch.app import create_app
from catwatch.extensions import db
from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.user.models import User
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.services import StripeCoupon


fake = Faker()
app = create_app()


def _log_status(count, model_label):
    """
    Log the output of how many records were created.

    :param count: The amount created
    :type count: int
    :param model_label: The name of the model
    :type model_label: str
    :return: None
    """
    click.echo('Created {0} {1}'.format(count, model_label))


def _bulk_insert(model, data, label):
    """
    Bulk insert data to a specific model and log it.

    :param model: The model
    :type model: SQLAlchemy
    :param data: The data to be saved
    :type data: list
    :param label: The label for the output
    :type label: str
    :return: None
    """
    with app.app_context():
        model.query.delete()
        db.session.commit()
        db.engine.execute(model.__table__.insert(), data)

        _log_status(model.query.count(), label)


@click.group()
def cli():
    """ Populate your db with generated data. """
    pass


@click.command()
def users():
    """
    Create random users.
    """
    random_emails = []
    data = []

    # Ensure we get about 49 unique random emails.
    for i in range(0, 49):
        random_emails.append(fake.email())
    random_emails = list(set(random_emails))

    while True:
        if len(random_emails) == 0:
            break

        params = {
            'role': random.choice(User.ROLE.keys()),
            'email': random_emails.pop(),
            'password': User.encrypt_password('password'),
            'name': fake.name()
        }

        data.append(params)

    _bulk_insert(User, data, 'users')


@click.command()
def issues():
    """
    Create random issues.
    """
    data = []

    for i in range(0, 50):
        params = {
            'status': random.choice(Issue.STATUS.keys()),
            'label': random.choice(Issue.LABEL.keys()),
            'email': fake.email(),
            'question': fake.paragraph()
        }

        data.append(params)

    _bulk_insert(Issue, data, 'issues')


@click.command()
def coupons():
    """
    Create random coupons (this actually creates them on Stripe too).
    """
    data = []

    for i in range(0, 5):
        random_pct = random.random()
        duration = random.choice(Coupon.DURATION.keys())

        # Create a fake unix timestamp in the future.
        redeem_by = fake.date_time_between(start_date='now',
                                           end_date='+1y').strftime('%s')

        # Bulk inserts need the same columns, so let's setup a few nulls.
        params = {
            'code': Coupon.random_coupon_code(),
            'duration': duration,
            'percent_off': None,
            'amount_off': None,
            'currency': None,
            'redeem_by': None,
            'max_redemptions': None,
            'duration_in_months': None,
        }

        if random_pct >= 0.5:
            params['percent_off'] = random.randint(1, 100)
            params['max_redemptions'] = random.randint(15, 50)
        else:
            params['amount_off'] = random.randint(1, 1337)
            params['currency'] = 'usd'

        if random_pct >= 0.75:
            params['redeem_by'] = redeem_by

        if duration == 'repeating':
            duration_in_months = random.randint(1, 12)
            params['duration_in_months'] = duration_in_months

        StripeCoupon.create(params)

        # Our database requires a Date object, not a unix timestamp.
        if redeem_by:
            params['redeem_by'] = datetime.utcfromtimestamp(float(redeem_by))\
                .strftime('%Y-%m-%d %H:%M:%S')

        if 'id' in params:
            params['code'] = params['id']
            del params['id']

        data.append(params)

    _bulk_insert(Coupon, data, 'coupons')


@click.command()
@click.pass_context
def all(ctx):
    """
    Populate everything at once.

    :param ctx:
    :return: None
    """
    ctx.invoke(users)
    ctx.invoke(issues)
    ctx.invoke(coupons)


cli.add_command(users)
cli.add_command(issues)
cli.add_command(coupons)
cli.add_command(all)
