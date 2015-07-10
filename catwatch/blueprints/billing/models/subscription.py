import datetime

import pytz

from config import settings
from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.extensions import db
from catwatch.blueprints.billing.models.credit_card import CreditCard
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.gateways.stripecom import Card as PaymentCard
from catwatch.blueprints.billing.gateways.stripecom import \
    Subscription as PaymentSubscription


class Subscription(ResourceMixin, db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Subscription details.
    plan = db.Column(db.String(128))
    coupon = db.Column(db.String(32))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Subscription, self).__init__(**kwargs)

    @classmethod
    def get_plan_by_id(cls, plan):
        """
        Pick the plan based on the plan identifier.

        :param plan: Plan identifier
        :type plan: str
        :return: dict or None
        """
        for key, value in settings.STRIPE_PLANS.iteritems():
            if value.get('id') == plan:
                return settings.STRIPE_PLANS[key]

        return None

    @classmethod
    def get_new_plan(cls, keys):
        """
        Pick the plan based on the plan identifier.

        :param keys: Keys to look through
        :type keys: list
        :return: str or None
        """
        for key in keys:
            split_key = key.split('submit_')

            if isinstance(split_key, list) and len(split_key) == 2:
                if Subscription.get_plan_by_id(split_key[1]):
                    return split_key[1]

        return None

    def create(self, user=None, name=None, plan=None, coupon=None, token=None):
        """
        Create a recurring subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param name: User's billing name
        :type name: str
        :param plan: Plan identifier
        :type plan: str
        :param coupon: Coupon code to apply
        :type coupon: str
        :param token: Token returned by javascript
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        if coupon:
            self.coupon = coupon.upper()

        customer = PaymentSubscription.create(token=token,
                                              email=user.email,
                                              plan=plan,
                                              coupon=self.coupon)

        # Update the user account.
        user.payment_id = customer.id
        user.name = name
        user.cancelled_subscription_on = None

        # Set the subscription details.
        self.user_id = user.id
        self.plan = plan

        # Redeem the coupon.
        if coupon:
            coupon = Coupon.query.filter(Coupon.code == self.coupon).first()
            coupon.redeem()

        # Create the credit card.
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        db.session.add(user)
        db.session.add(credit_card)
        db.session.add(self)

        db.session.commit()

        return True

    def update(self, user=None, coupon=None, plan=None):
        """
        Update an existing subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param coupon: Coupon code to apply
        :type coupon: str
        :param plan: Plan identifier
        :type plan: str
        :return: bool
        """
        PaymentSubscription.update(user.payment_id, coupon, plan)

        user.subscription.plan = plan
        if coupon:
            user.subscription.coupon = coupon
            coupon = Coupon.query.filter(Coupon.code == coupon).first()

            if coupon:
                coupon.redeem()

        db.session.add(user.subscription)
        db.session.commit()

        return True

    def cancel(self, user=None, discard_credit_card=True):
        """
        Cancel an existing subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param discard_credit_card: Delete the user's credit card
        :type discard_credit_card: bool
        :return: bool
        """
        PaymentSubscription.cancel(user.payment_id)

        user.payment_id = None
        user.cancelled_subscription_on = datetime.datetime.now(pytz.utc)

        db.session.add(user)
        db.session.delete(user.subscription)

        # Explicitly delete the credit card because the FK is on the
        # user, not subscription so we can't depend on cascading deletes.
        # This is for cases where you may want to keep a user's card
        # on file even if they cancelled.
        if discard_credit_card:
            db.session.delete(user.credit_card)

        db.session.commit()

        return True

    def update_payment_method(self, user=None, name=None, token=None):
        """
        Update the subscription.

        :param user: User to apply the subscription to
        :type user: User instance
        :param name: User's billing name
        :type name: str
        :param token: Token returned by javascript
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        customer = PaymentCard.update(user.payment_id, token)
        user.name = name

        # Create the new credit card.
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        db.session.add(user)
        db.session.delete(user.credit_card)
        db.session.add(credit_card)

        db.session.commit()

        return True
