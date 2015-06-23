from flask import url_for
from flask_babel import ngettext as _n
from flask_babel import gettext as _

from catwatch.tests.lib.util import ViewTestMixin
from catwatch.tests.lib.assertions import assert_status_with_message
from catwatch.blueprints.user.models import User
from catwatch.blueprints.issue.models import Issue


class TestDashboard(ViewTestMixin):
    def test_dashboard_page(self):
        self.login()
        response = self.client.get(url_for('admin.dashboard'))

        assert 'Billing' in response.data
        assert 'Subscriptions' in response.data
        assert 'Coupons' in response.data
        assert 'User' in response.data
        assert 'Issue' in response.data


class TestUsers(ViewTestMixin):
    def test_index_page(self):
        """ Index renders successfully. """
        self.login()
        response = self.client.get(url_for('admin.users'))

        assert response.status_code == 200

    def test_edit_page(self):
        """ Edit page renders successfully. """
        self.login()
        response = self.client.get(url_for('admin.users_edit', id=1))

        assert_status_with_message(200, response, 'admin@localhost.com')

    def test_edit_resource(self):
        """ Edit this resource successfully. """
        params = {
            'role': 'admin',
            'username': 'foo',
            'active': True
        }

        self.login()
        response = self.client.post(url_for('admin.users_edit', id=1),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('User has been saved successfully.'))

    def test_bulk_delete_nothing(self):
        """ Last admin account should not get deleted. """
        old_count = User.query.count()
        params = {
            'bulk_ids': [1],
            'scope': 'all_selected_products'
        }

        self.login()
        response = self.client.post(url_for('admin.users_bulk_delete'),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _n('%(num)d user was scheduled to be '
                                      'deleted.',
                                      '%(num)d users were scheduled to be '
                                      'deleted.', num=0))

        new_count = User.query.count()
        assert old_count == new_count

    def test_cancel_subscription(self, subscriptions, mock_stripe):
        """ User subscription gets cancelled.. """
        user = User.find_by_identity('subscriber@localhost.com')
        params = {
            'id': user.id
        }

        self.login()
        response = self.client.post(url_for('admin.users_cancel_subscription'),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Subscription has been cancelled for '
                                     '%(user)s', user='Subby'))
        assert user.cancelled_subscription_on is not None


class TestIssues(ViewTestMixin):
    def test_index_page(self):
        """ Index renders successfully. """
        self.login()
        response = self.client.get(url_for('admin.issues'))

        assert response.status_code == 200

    def test_edit_page(self, issues):
        """ Edit page renders successfully. """
        self.login()
        response = self.client.get(url_for('admin.issues_edit', id=1))

        assert_status_with_message(200, response, 'admin@localhost.com')

    def test_edit_resource(self):
        """ Edit this resource successfully. """
        params = {
            'label': 'signup',
            'email': 'foo@bar.com',
            'question': 'Cool.',
            'status': 'open',
        }

        issue = Issue(**params)
        issue.save()

        params_edit = {
            'label': 'other',
            'email': 'foo@bar.com',
            'question': 'Cool.',
            'status': 'closed',
        }

        self.login()
        response = self.client.post(url_for('admin.issues_edit', id=issue.id),
                                    data=params_edit, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Issue has been saved successfully.'))

    def test_bulk_delete(self, issues):
        """ Resource gets bulk deleted. """
        old_count = Issue.query.count()
        params = {
            'bulk_ids': [1, 2],
            'scope': 'all_search_results'
        }

        self.login()
        response = self.client.post(url_for('admin.issues_bulk_delete'),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _n('%(num)d issue was deleted.',
                                      '%(num)d issues were deleted.',
                                      num=2))

        new_count = Issue.query.count()
        assert (old_count - 2) == new_count


class TestCoupon(ViewTestMixin):
    def test_index_page(self):
        """ Index renders successfully. """
        self.login()
        response = self.client.get(url_for('admin.coupons'))

        assert response.status_code == 200

    def test_new_page(self, coupons):
        """ New page renders successfully. """
        self.login()
        response = self.client.get(url_for('admin.coupons_new'))

        assert response.status_code == 200

    def test_new_resource(self, mock_stripe):
        """ Edit this resource successfully. """
        params = {
            'code': '1337',
            'duration': 'repeating',
            'percent_off': 5,
            'amount_off': None,
            'currency': 'usd',
            'redeem_by': None,
            'max_redemptions': 10,
            'duration_in_months': 5,
        }

        self.login()
        response = self.client.post(url_for('admin.coupons_new'),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Coupon has been created successfully.'))

    def test_bulk_delete(self, coupons, mock_stripe):
        """ Resource gets bulk deleted. """
        params = {
            'bulk_ids': [1, 2, 3],
            'scope': 'all_search_results'
        }

        self.login()
        response = self.client.post(url_for('admin.coupons_bulk_delete'),
                                    data=params, follow_redirects=True)

        assert_status_with_message(200, response,
                                   _n('%(num)d coupon was scheduled to be '
                                      'deleted.',
                                      '%(num)d coupons were scheduled to be '
                                      'deleted.', num=3))
