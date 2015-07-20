import logging
import random
from datetime import datetime

import click
from faker import Faker

SEED_ADMIN_EMAIL = None
ACCEPT_LANGUAGES = None

try:
    from instance import settings

    SEED_ADMIN_EMAIL = settings.SEED_ADMIN_EMAIL
    ACCEPT_LANGUAGES = settings.ACCEPT_LANGUAGES
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    if SEED_ADMIN_EMAIL is None:
        SEED_ADMIN_EMAIL = settings.SEED_ADMIN_EMAIL

    if ACCEPT_LANGUAGES is None:
        ACCEPT_LANGUAGES = settings.ACCEPT_LANGUAGES

from catwatch.app import create_app
from catwatch.extensions import db
from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.user.models import User
from catwatch.blueprints.billing.models.invoice import Invoice
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.gateways.stripecom import \
    Coupon as PaymentCoupon

fake = Faker()
app = create_app()
db.app = app


def _log_status(count, model_label):
    """
    Log the output of how many records were created.

    :param count: Amount created
    :type count: int
    :param model_label: Name of the model
    :type model_label: str
    :return: None
    """
    click.echo('Created {0} {1}'.format(count, model_label))

    return None


def _bulk_insert(model, data, label):
    """
    Bulk insert data to a specific model and log it.

    :param model: Model being affected
    :type model: SQLAlchemy
    :param data: Data to be saved
    :type data: list
    :param label: Label for the output
    :type label: str
    :return: None
    """
    with app.app_context():
        model.query.delete()
        db.session.commit()
        db.engine.execute(model.__table__.insert(), data)

        _log_status(model.query.count(), label)

    return None


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

    # Ensure we get about 50 unique random emails, +1 due to the seeded email.
    for i in range(0, 49):
        random_emails.append(fake.email())

    random_emails.append(SEED_ADMIN_EMAIL)
    random_emails = list(set(random_emails))

    while True:
        if len(random_emails) == 0:
            break

        email = random_emails.pop()

        params = {
            'role': random.choice(User.ROLE.keys()),
            'email': email,
            'password': User.encrypt_password('password'),
            'name': fake.name(),
            'locale': random.choice(ACCEPT_LANGUAGES)
        }

        # Ensure the seeded admin is always an admin.
        if email == SEED_ADMIN_EMAIL:
            params['role'] = 'admin'
            params['locale'] = 'en'

        data.append(params)

    return _bulk_insert(User, data, 'users')


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

    return _bulk_insert(Issue, data, 'issues')


@click.command()
def coupons():
    """
    Create random coupons.
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

        PaymentCoupon.create(**params)

        # Our database requires a Date object, not a unix timestamp.
        if redeem_by:
            params['redeem_by'] = datetime.utcfromtimestamp(float(redeem_by)) \
                .strftime('%Y-%m-%dT%H:%M:%S Z')

        if 'id' in params:
            params['code'] = params.get('id')
            del params['id']

        data.append(params)

    return _bulk_insert(Coupon, data, 'coupons')


@click.command()
def invoices():
    """
    Create random invoices.
    """
    data = []

    users = db.session.query(User).all()

    for user in users:
        for i in range(0, random.randint(1, 12)):
            # Create a fake unix timestamp in the future.
            created_on = fake.date_time_between(
                start_date='-1y', end_date='now').strftime('%s')
            period_start_on = fake.date_time_between(
                start_date='now', end_date='+1y').strftime('%s')
            period_end_on = fake.date_time_between(
                start_date=period_start_on, end_date='+14d').strftime('%s')
            exp_date = fake.date_time_between(
                start_date='now', end_date='+2y').strftime('%s')

            created_on = datetime.utcfromtimestamp(
                float(created_on)).strftime('%Y-%m-%dT%H:%M:%S Z')
            period_start_on = datetime.utcfromtimestamp(
                float(period_start_on)).strftime('%Y-%m-%d')
            period_end_on = datetime.utcfromtimestamp(
                float(period_end_on)).strftime('%Y-%m-%d')
            exp_date = datetime.utcfromtimestamp(
                float(exp_date)).strftime('%Y-%m-%d')

            plans = ['BRONZE', 'GOLD', 'PLATINUM']
            cards = ['Visa', 'Mastercard', 'AMEX',
                     'J.C.B', "Diner's Club"]

            params = {
                'created_on': created_on,
                'updated_on': created_on,
                'user_id': user.id,
                'receipt_number': fake.md5(),
                'description': '{0} MONTHLY'.format(random.choice(plans)),
                'period_start_on': period_start_on,
                'period_end_on': period_end_on,
                'currency': 'usd',
                'tax': random.random() * 100,
                'tax_percent': random.random() * 10,
                'total': random.random() * 1000,
                'brand': random.choice(cards),
                'last4': random.randint(1000, 9000),
                'exp_date': exp_date
            }

            data.append(params)

    return _bulk_insert(Invoice, data, 'invoices')


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
    ctx.invoke(invoices)

    return None


cli.add_command(users)
cli.add_command(issues)
cli.add_command(coupons)
cli.add_command(invoices)
cli.add_command(all)
