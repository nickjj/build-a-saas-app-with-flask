import logging

import stripe


class Stripe(object):
    pass


class StripeCoupon(Stripe):
    @classmethod
    def create(cls, params):
        """
        Create a new coupon, it expects the following call signature:
          params = {
            'code': '10PCTOFF',       # Random one will be generated if skipped
            'duration': 'forever',    # Default
            'amount_off': 0,          # Amount_off or percent_off, not both
            'percent_off: 10,         # Amount_off or percent_off, not both
            'currency': 'usd',        # Only required if amount_off is set
            'duration_in_months',     # Applicable if duration is not forever
            'max_redemptions': null,
            'redeem_by': null         # Unix timestamp
          }
          StripeCoupon.create(params)

        API Documentation:
          https://stripe.com/docs/api#create_coupon

        :param params: Parameters requested by the Stripe API
        :type params: dict
        :return: Stripe coupon object
        """
        params['id'] = params['code']
        del params['code']

        return stripe.Coupon.create(**params)

    @classmethod
    def delete(cls, id):
        """
        Delete a coupon.

        API Documentation:
          https://stripe.com/docs/api#delete_coupon

        :param id: Coupon code
        :type id: str
        :return: Stripe object
        """
        coupon = stripe.Coupon.retrieve(id)

        return coupon.delete()


class StripeEvent(Stripe):
    @classmethod
    def retrieve(cls, event_id):
        """
        Retrieve an event, this is used to validate the event in attempt to
        protect us from potentially malicious events not sent from Stripe.

        API Documentation:
          https://stripe.com/docs/api#retrieve_event

        :param event_id: Stripe event id
        :type event_id: int

        :return: Stripe event object
        """
        return stripe.Event.retrieve(event_id)


class StripeCard(Stripe):
    @classmethod
    def update(cls, customer_id, stripe_token=None):
        """
        Update an existing card through a customer.

        API Documentation:
          https://stripe.com/docs/api/python#update_card

        :param customer_id: Stripe customer id
        :type customer_id: int
        :param stripe_token: Stripe token
        :type stripe_token: str
        :return: Stripe customer object
        """
        customer = stripe.Customer.retrieve(customer_id)

        customer.source = stripe_token
        return customer.save()


class StripeSubscription(Stripe):
    @classmethod
    def create(cls, params):
        """
        Create a new subscription, it expects the following call signature:
          params = {
            'source': 'the_stripe_token',
            'email': 'foo@bar.com',
            'coupon': '10PCTOFF',         # Optional
            'plan': 'gold'
          }
          StripeSubscription.create(params)

        API Documentation:
          https://stripe.com/docs/api#create_subscription

        :param params: Parameters requested by the Stripe API
        :type params: dict
        :return: Stripe customer object
        """
        return stripe.Customer.create(**params)

    @classmethod
    def update(cls, params):
        """
        Update a subscription, it expects the following call signature:
          params = {
            'customer_id': 'the_stripe_token',
            'plan': 'gold',
            'coupon': '10PCTOFF',              # Optional
          }
          StripeSubscription.update(params)

        API Documentation:
          https://stripe.com/docs/api/python#update_subscription

        :param params: Parameters requested by the Stripe API
        :type params: dict
        :return: Stripe subscription object
        """
        customer = stripe.Customer.retrieve(params['customer_id'])
        subscription_id = customer.subscriptions.data[0].id
        subscription = customer.subscriptions.retrieve(subscription_id)

        subscription.plan = params['plan']

        if params['coupon']:
            subscription.coupon = params['coupon']

        return subscription.save()

    @classmethod
    def cancel(cls, customer_id=None):
        """
        Cancel an existing subscription.

        API Documentation:
          https://stripe.com/docs/api#cancel_subscription

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe subscription object
        """
        customer = stripe.Customer.retrieve(customer_id)
        subscription_id = customer.subscriptions.data[0].id

        return customer.subscriptions.retrieve(subscription_id).delete()


class StripePlan(Stripe):
    @classmethod
    def retrieve(cls, plan_id):
        """
        Retrieve an existing plan.

        API Documentation:
          https://stripe.com/docs/api#retrieve_plan

        :param plan_id: Plan ID
        :type plan_id: str
        :return: Stripe plan object
        """
        try:
            return stripe.Plan.retrieve(plan_id)
        except stripe.error.StripeError as e:
            logging.error(e)

    @classmethod
    def list(cls):
        """
        List existing plans.

        API Documentation:
          https://stripe.com/docs/api#list_plans

        :return: Stripe plans object
        """
        try:
            return stripe.Plan.all()
        except stripe.error.StripeError as e:
            logging.error(e)

    @classmethod
    def create(cls, params):
        """
        Create a new plan, it expects the following call signature:
          params = {
            'id': 'bronze',
            'name': 'Bronze',
            'amount': 100,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 14,
            'statement_descriptor': 'Bronze monthly',
            'metadata': {}
          }
          StripePlan.create(params)

        API Documentation:
          https://stripe.com/docs/api#create_plan

        :param params: Parameters requested by the Stripe API
        :type params: dict
        :return: Stripe plan object
        """
        allowed_params = (
            'id', 'name', 'amount', 'currency', 'interval', 'interval_count',
            'trial_period_days', 'statement_descriptor', 'metadata')
        stripe_params = StripePlan._whitelist_params(params, allowed_params)

        try:
            return stripe.Plan.create(**stripe_params)
        except stripe.error.StripeError as e:
            logging.error(e)

    @classmethod
    def update(cls, params):
        """
        Update an existing plan, it expects the following call signature:
          params = {
            'name': 'Bronze',
            'statement_descriptor': 'Bronze monthly',
            'metadata': {}
          }
          StripePlan.update(params)

        API Documentation:
          https://stripe.com/docs/api#update_plan

        :param params: Parameters requested by the Stripe API
        :type params: dict
        :return: Stripe plan object
        """
        allowed_params = ('name', 'statement_descriptor', 'metadata')
        stripe_params = StripePlan._whitelist_params(params, allowed_params)

        try:
            plan = stripe.Plan.retrieve(params['id'])

            for param in allowed_params:
                if stripe_params.get(param, None):
                    plan[param] = stripe_params[param]

            return plan.save()
        except stripe.error.StripeError as e:
            logging.error(e)

    @classmethod
    def delete(cls, plan_id):
        """
        Delete an existing plan.

        API Documentation:
          https://stripe.com/docs/api#delete_plan

        :param plan_id: Plan ID
        :type plan_id: str
        :return: Stripe plan object
        """
        try:
            plan = stripe.Plan.retrieve(plan_id)
            return plan.delete()
        except stripe.error.StripeError as e:
            logging.error(e)

    @classmethod
    def _whitelist_params(cls, original_params, allowed_params):
        """
        Return a new dict that has only white listed params.

        :param original_params: Original params.
        :type original_params: dict
        :param allowed_params:  Whitelist of allowed params.
        :type allowed_params: tuple
        :return: dict
        """
        stripe_params = original_params.copy()

        for param in original_params:
            if param not in allowed_params:
                del stripe_params[param]

        return stripe_params


class StripeInvoice(Stripe):
    @classmethod
    def upcoming(cls, customer_id):
        """
        Retrieve an upcoming invoice item for a user.

        API Documentation:
          https://stripe.com/docs/api#retrieve_customer_invoice

        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe invoice object
        """
        return stripe.Invoice.upcoming(customer=customer_id)
