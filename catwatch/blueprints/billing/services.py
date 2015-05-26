import logging

import stripe


class Stripe(object):
    pass


class StripeCard(object):
    @classmethod
    def update(cls, customer_id, token=None):
        pass


class StripeSubscription(Stripe):
    @classmethod
    def create(cls, params):
        """
        Create a new subscription, it expects the following call signature:
          params = {
            'source': 'the_stripe_token',
            'email': 'foo@bar.com',
            'plan': 'gold'
          }
          Stripe.create_subscription(params)

        API Documentation:
          https://stripe.com/docs/api#create_subscription

        :param params: Parameters requested by the Stripe API
        :type params: dict
        :return: Stripe customer object
        """
        return stripe.Customer.create(**params)

    @classmethod
    def update(cls, customer_id=None, plan=None):
        pass

    @classmethod
    def cancel(cls, customer_id=None):
        pass


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
          Stripe.create_plan(params)

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
          Stripe.update_plan(params)

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
