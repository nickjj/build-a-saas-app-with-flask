import datetime

from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.extensions import db


class Money(object):
    @classmethod
    def cents_to_dollars(cls, cents):
        """
        Convert cents to dollars.

        :param cents: Amount in cents
        :type cents: int
        :return: float
        """
        return round(cents / 100.0, 2)

    @classmethod
    def dollars_to_cents(cls, dollars):
        """
        Convert dollars to cents.

        :param dollars: Amount in dollars
        :type dollars: float
        :return: int
        """
        return int(dollars * 100)


class CreditCard(ResourceMixin, db.Model):
    IS_EXPIRING_THRESHOLD_MONTHS = 2

    __tablename__ = 'credit_cards'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Card details.
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)
    is_expiring = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(CreditCard, self).__init__(**kwargs)

    @classmethod
    def is_expiring_soon(cls, exp_date):
        """
        Determine whether or not this credit card is expiring soon.

        :param exp_date: Expiration date
        :type exp_date: date
        :return: bool
        """
        today = datetime.date.today()
        delta = CreditCard.IS_EXPIRING_THRESHOLD_MONTHS * 365 / 12
        today_with_delta = today + datetime.timedelta(delta)

        return exp_date <= today_with_delta

    @classmethod
    def extract_card_params(cls, stripe_customer):
        """
        Extract the credit card info from a stripe customer object.

        :param stripe_customer: Stripe customer
        :type stripe_customer: Stripe customer
        :return: Credit card dict
        """
        card_data = stripe_customer.cards.data[0]
        exp_date = datetime.date(card_data.exp_year, card_data.exp_month, 1)

        card = {
            'brand': card_data.brand,
            'last4': card_data.last4,
            'exp_date': exp_date,
            'is_expiring': CreditCard.is_expiring_soon(exp_date)
        }

        return card
