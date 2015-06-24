import datetime

import pytest
import pytz
from mock import Mock

from config import settings
from catwatch.app import create_app
from catwatch.lib.util_datetime import timedelta_months
from catwatch.extensions import db as _db
from catwatch.blueprints.user.models import User
from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.billing.models.credit_card import CreditCard
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.models.subscription import Subscription
from catwatch.blueprints.billing.gateways.stripecom import \
    Coupon as PaymentCoupon
from catwatch.blueprints.billing.gateways.stripecom import \
    Event as PaymentEvent
from catwatch.blueprints.billing.gateways.stripecom import Card as PaymentCard
from catwatch.blueprints.billing.gateways.stripecom import \
    Subscription as PaymentSubscription
from catwatch.blueprints.billing.gateways.stripecom import \
    Invoice as PaymentInvoice


# App and database fixtures ---------------------------------------------------
@pytest.yield_fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    db_uri = '{0}_test'.format(settings.SQLALCHEMY_DATABASE_URI)
    params = {
        'DEBUG': False,
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': db_uri
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Setup our database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    # Create a single user because a lot of tests do not mutate this user.
    # It will result in quite a bit faster tests.
    params = {
        'role': 'admin',
        'email': 'admin@localhost.com',
        'name': 'Dev',
        'password': 'password'
    }

    admin = User(**params)

    _db.session.add(admin)
    _db.session.commit()

    return _db


@pytest.yield_fixture(scope='function')
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and postgres does.

    Read more about this at:
    http://stackoverflow.com/a/26624146

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


# Model fixtures --------------------------------------------------------------
@pytest.fixture(scope='session')
def token(db):
    """
    Serialize a JWS token.

    :param db: Pytest fixture
    :return: JWS token
    """
    user = User.find_by_identity('admin@localhost.com')
    return user.serialize_token()


@pytest.fixture(scope='function')
def users(db):
    """
    Create user fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(User).delete()

    users = [
        {
            'role': 'admin',
            'email': 'admin@localhost.com',
            'password': 'password'
        },
        {
            'active': False,
            'email': 'disabled@localhost.com',
            'password': 'password'
        }
    ]

    for user in users:
        db.session.add(User(**user))

    db.session.commit()

    return db


@pytest.fixture(scope='function')
def issues(db):
    """
    Create issue fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(Issue).delete()

    issues = [
        {
            'label': 'login',
            'email': 'admin@localhost.com',
            'question': '42.',
            'status': 'unread'
        },
        {
            'label': 'billing',
            'email': 'admin@localhost.com',
            'question': 'Hello.',
            'status': 'unread'
        }
    ]

    for issue in issues:
        db.session.add(Issue(**issue))

    db.session.commit()

    return db


@pytest.fixture(scope='function')
def credit_cards(db):
    """
    Create credit card fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(CreditCard).delete()

    may_29_2015 = datetime.date(2015, 05, 29)
    june_29_2015 = datetime.datetime(2015, 06, 29, 0, 0, 0)
    june_29_2015 = pytz.utc.localize(june_29_2015)

    credit_cards = [
        {
            'user_id': 1,
            'brand': 'Visa',
            'last4': 4242,
            'exp_date': june_29_2015
        },
        {
            'user_id': 1,
            'brand': 'Visa',
            'last4': 4242,
            'exp_date': timedelta_months(12, may_29_2015)
        }
    ]

    for card in credit_cards:
        db.session.add(CreditCard(**card))

    db.session.commit()

    return db


@pytest.fixture(scope='function')
def coupons(db):
    """
    Create coupon fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(Coupon).delete()

    may_29_2015 = datetime.datetime(2015, 05, 29, 0, 0, 0)
    may_29_2015 = pytz.utc.localize(may_29_2015)

    june_29_2015 = datetime.datetime(2015, 06, 29)
    june_29_2015 = pytz.utc.localize(june_29_2015)

    coupons = [
        {
            'amount_off': 1,
            'redeem_by': may_29_2015
        },
        {
            'amount_off': 1,
            'redeem_by': june_29_2015
        },
        {
            'amount_off': 1
        }
    ]

    for coupon in coupons:
        db.session.add(Coupon(**coupon))

    db.session.commit()

    return db


@pytest.fixture(scope='function')
def subscriptions(db):
    """
    Create subscription fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    subscriber = User.find_by_identity('subscriber@localhost.com')
    if subscriber:
        subscriber.delete()
    db.session.query(Subscription).delete()

    params = {
        'role': 'admin',
        'email': 'subscriber@localhost.com',
        'name': 'Subby',
        'password': 'password',
        'payment_id': 'cus_000'
    }

    admin = User(**params)

    # The account needs to be commit before we can assign a subscription to it.
    db.session.add(admin)
    db.session.commit()

    # Create a subscription.
    params = {
        'user_id': admin.id,
        'plan': 'gold'
    }
    subscription = Subscription(**params)
    db.session.add(subscription)

    # Create a credit card.
    params = {
        'user_id': admin.id,
        'brand': 'Visa',
        'last4': '4242',
        'exp_date': datetime.date(2015, 06, 01)
    }
    credit_card = CreditCard(**params)
    db.session.add(credit_card)

    db.session.commit()

    return db


# Service fixtures ------------------------------------------------------------
@pytest.fixture(scope='session')
def mock_stripe():
    """
    Mock all of the Stripe API calls.

    :return:
    """
    PaymentCoupon.create = Mock(return_value={})
    PaymentCoupon.delete = Mock(return_value={})
    PaymentEvent.retrieve = Mock(return_value={})
    PaymentCard.update = Mock(return_value={})
    PaymentSubscription.create = Mock(return_value={})
    PaymentSubscription.update = Mock(return_value={})
    PaymentSubscription.cancel = Mock(return_value={})

    upcoming_api = {
        'date': 1433018770,
        'id': 'in_000',
        'period_start': 1433018770,
        'period_end': 1433018770,
        'lines': {
            'data': [
                {
                    'id': 'sub_000',
                    'object': 'line_item',
                    'type': 'subscription',
                    'livemode': True,
                    'amount': 0,
                    'currency': 'usd',
                    'proration': False,
                    'period': {
                        'start': 1433161742,
                        'end': 1434371342
                    },
                    'subscription': None,
                    'quantity': 1,
                    'plan': {
                        'interval': 'month',
                        'name': 'Gold',
                        'created': 1424879591,
                        'amount': 500,
                        'currency': 'usd',
                        'id': 'gold',
                        'object': 'plan',
                        'livemode': False,
                        'interval_count': 1,
                        'trial_period_days': 14,
                        'metadata': {
                        },
                        'statement_descriptor': 'GOLD MONTHLY'
                    },
                    'description': None,
                    'discountable': True,
                    'metadata': {
                    }
                }
            ],
            'total_count': 1,
            'object': 'list',
            'url': '/v1/invoices/in_000/lines'
        },
        'subtotal': 0,
        'total': 0,
        'customer': 'cus_000',
        'object': 'invoice',
        'attempted': True,
        'closed': True,
        'forgiven': False,
        'paid': True,
        'livemode': False,
        'attempt_count': 0,
        'amount_due': 500,
        'currency': 'usd',
        'starting_balance': 0,
        'ending_balance': 0,
        'next_payment_attempt': None,
        'webhooks_delivered_at': None,
        'charge': None,
        'discount': None,
        'application_fee': None,
        'subscription': 'sub_000',
        'tax_percent': None,
        'tax': None,
        'metadata': {
        },
        'statement_descriptor': None,
        'description': None,
        'receipt_number': None
    }
    PaymentInvoice.upcoming = Mock(return_value=upcoming_api)
