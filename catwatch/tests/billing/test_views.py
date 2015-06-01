from flask import url_for, json
from flask_babel import gettext as _

from catwatch.tests.lib.util import ViewTestMixin
from catwatch.tests.lib.assertions import assert_status_with_message


class TestBilling(ViewTestMixin):
    def test_pricing_page(self):
        """ Pricing page renders successfully. """
        response = self.client.get(url_for('billing.pricing'))
        assert_status_with_message(200, response, 'Sign up')

    def test_pricing_page_logged_in(self):
        """ Pricing page renders successfully. """
        self.login()

        response = self.client.get(url_for('billing.pricing'))
        assert_status_with_message(200, response, 'Continue')

    def test_pricing_page_as_subscriber(self, subscriptions):
        """ Pricing page for subscribers should redirect to update. """
        self.login(identity='subscriber@localhost.com')

        response = self.client.get(url_for('billing.pricing'),
                                   follow_redirects=True)

        assert_status_with_message(200, response, 'Change plan')

    def test_coupon_code_not_valid(self):
        """ Coupon code should not be processed, """
        self.login()

        params = {'coupon_code': None}
        response = self.client.post(url_for('billing.coupon_code'),
                                    data=params, follow_redirects=True)

        data = json.loads(response.data)

        assert response.status_code == 422
        assert data['error'] == _('Discount code cannot be processed.')

    def test_coupon_code_not_redeemable(self):
        """ Coupon code should be redeemable. """
        self.login()

        params = {'coupon_code': 'foo'}
        response = self.client.post(url_for('billing.coupon_code'),
                                    data=params, follow_redirects=True)

        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['error'] == _('Discount code not found.')

    def test_subscription_create_page(self):
        """ Subscription create page renders successfully. """
        self.login()

        response = self.client.get(url_for('billing.create'),
                                   follow_redirects=True)

        assert response.status_code == 200

    def test_subscription_create_as_subscriber(self, subscriptions):
        """ Subscribers should not be allowed to create a subscription. """
        self.login(identity='subscriber@localhost.com')

        response = self.client.get(url_for('billing.create'),
                                   follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('You already have an active subscription'
                                     '.'))

    def test_subscription_create(self, users, mock_stripe):
        """ Subscription create requires javascript. """
        self.login()

        params = {
            'stripe_key': 'cus_000',
            'plan': 'gold',
            'name': 'Foobar Johnson'
        }

        response = self.client.post(url_for('billing.create'),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('You must enable Javascript for this '
                                     'request.'))

    def test_subscription_update_page_without_subscription(self):
        """ Subscription update page redirects to pricing page. """
        self.login()

        response = self.client.get(url_for('billing.update'),
                                   follow_redirects=True)

        assert_status_with_message(200, response, "You're moments away")

    def test_subscription_update_page(self, subscriptions):
        """ Subscription update page renders successfully. """
        self.login(identity='subscriber@localhost.com')

        response = self.client.get(url_for('billing.update'),
                                   follow_redirects=True)

        assert_status_with_message(200, response,
                                   "You're about to change plans")

    def test_subscription_update(self, subscriptions, mock_stripe):
        """ Subscription create adds a new subscription. """
        self.login(identity='subscriber@localhost.com')

        params = {
            'submit_gold': ''
        }

        response = self.client.post(url_for('billing.update'),
                                    data=params, follow_redirects=True)

        assert response.status_code == 200

    def test_subscription_cancel_page_without_subscription(self):
        """ Subscription cancel page redirects to settings. """
        self.login()

        response = self.client.get(url_for('billing.cancel'),
                                   follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('You do not have an active subscription'
                                     '.'))

    def test_subscription_cancel_page(self, subscriptions):
        """ Subscription cancel page renders successfully. """
        self.login(identity='subscriber@localhost.com')

        response = self.client.get(url_for('billing.cancel'),
                                   follow_redirects=True)

        assert response.status_code == 200

    def test_subscription_cancel(self, subscriptions, mock_stripe):
        """ Subscription cancel is successful. """
        self.login(identity='subscriber@localhost.com')

        response = self.client.post(url_for('billing.cancel'),
                                    data={}, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Sorry to see you go, your subscription '
                                     'has been cancelled.'))

    def test_subscription_update_payment_method_without_card(self):
        """ Subscription update method without card should fail. """
        self.login()
        response = self.client.post(url_for('billing.update_payment_method'),
                                    data={}, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('You do not have a payment method on '
                                     'file.'))

    def test_subscription_update_payment_method(self, subscriptions,
                                                mock_stripe):
        """ Subscription update payment requires javascript. """
        self.login(identity='subscriber@localhost.com')
        response = self.client.post(url_for('billing.update_payment_method'),
                                    data={}, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('You must enable Javascript for this '
                                     'request.'))

    def test_subscription_billing_history(self, subscriptions, mock_stripe):
        """ Subscription billing history should render successfully. """
        self.login(identity='subscriber@localhost.com')
        response = self.client.get(url_for('billing.billing_history'))

        assert_status_with_message(200, response,
                                   'Billing details and history')

    def test_subscription_billing_history_without_sub(self, mock_stripe):
        """ Subscription billing history without sub should still work. """
        self.login()
        response = self.client.get(url_for('billing.billing_history'))

        assert_status_with_message(200, response,
                                   'Billing details and history')
