import datetime

from config import settings
from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.extensions import db
from catwatch.blueprints.billing.models.credit_card import CreditCard
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.services import StripeCard, StripeSubscription


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
        """
        For creation, it expects the following call signature:
          params = {
            'user': User object (ie. current_user),
            'name': 'Mr or Mrs. Foo',
            'plan': 'gold',
            'coupon': '10PCTOFF',
            'source': 'the_stripe_token'
          }
          subscription = Subscription(**params)
          subscription.create()

        or, for updating:

        params = {
            'user': User object (ie. current_user),
            'plan': 'bronze'
        }
        subscription = Subscription(**params)
        subscription.update()

        or, for cancelling:

          params = {
            'user': User object (ie. current_user)
          }
          subscription = Subscription(**params)
          subscription.cancel()

        :param user: Subscriber's user account
        :type user: User
        :param name: Subscriber's full name
        :type name: str
        :param plan: Subscriber's plan
        :type plan: str
        :param source: Stripe token
        :type source: str
        :return: Subscription
        """
        self.params = kwargs

        self.user_id = kwargs['user'].id

        if kwargs.get('plan', None):
            self.plan = kwargs['plan']

        if kwargs.get('coupon', None):
            self.coupon = kwargs['coupon']

        super(Subscription, self).__init__(user_id=self.user_id,
                                           plan=self.plan,
                                           coupon=self.coupon)

    @classmethod
    def get_plan_by_stripe_id(cls, id):
        """
        Pick the plan based on the Stripe ID.

        :param id: Stripe ID
        :type id: str
        :return: Dict of the plan or None
        """
        for key, value in settings.STRIPE_PLANS.iteritems():
            if value['id'] == id:
                return settings.STRIPE_PLANS[key]

        return None

    def create(self):
        """
        Return whether or not the subscription was created successfully.

        :return: bool
        """
        if self.params['stripe_token'] is None:
            return False

        user = self.params['user']

        # Create the customer on Stripe's end.
        stripe_params = {
            'source': self.params['stripe_token'],
            'email': user.email,
            'plan': self.plan,
            'coupon': self.coupon
        }
        customer = StripeSubscription.create(stripe_params)

        # Update the user account.
        user.stripe_customer_id = customer.id
        user.name = self.params['name']
        user.cancelled_subscription_on = None

        # Create the credit card.
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        # Redeem the coupon.
        if self.coupon:
            coupon = Coupon.query.filter(Coupon.code == self.coupon).first()
            coupon.redeem()

        db.session.add(user)
        db.session.add(credit_card)
        db.session.add(self)

        db.session.commit()

        return True

    def update(self):
        """
        Return whether or not the subscription was updated successfully.

        :return: bool
        """
        user = self.params['user']

        # Update the subscription on Stripe's end
        stripe_params = {
            'customer_id': user.stripe_customer_id,
            'plan': self.plan,
            'coupon': self.coupon
        }

        StripeSubscription.update(stripe_params)

        user.subscription.plan = self.plan
        if self.coupon:
            user.subscription.coupon = self.coupon
            coupon = Coupon.query.filter(Coupon.code == self.coupon).first()
            coupon.redeem()

        db.session.add(user.subscription)
        db.session.commit()

        return True

    def cancel(self, discard_credit_card=True):
        """
        Return whether or not the subscription was cancelled successfully.

        :param at_period_end: If true, delete the user's credit card
        :type at_period_end: bool
        :return: bool
        """
        user = self.params['user']

        StripeSubscription.cancel(user.stripe_customer_id)

        # Update the user account.
        user.stripe_customer_id = None
        user.cancelled_subscription_on = datetime.datetime.utcnow()

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

    def update_payment_method(self):
        """
        Return whether or not the subscription payment method
        was updated successfully.

        :return: bool
        """
        if self.params['stripe_token'] is None:
            return False

        user = self.params['user']

        customer = StripeCard.update(user.stripe_customer_id,
                                     self.params['stripe_token'])

        user.name = self.params['name']

        # Create the new credit card.
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        db.session.add(user)
        db.session.delete(user.credit_card)
        db.session.add(credit_card)

        db.session.commit()

        return True
