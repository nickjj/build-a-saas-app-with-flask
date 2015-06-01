from flask import url_for
from flask_babel import gettext as _

from catwatch.tests.lib.util import ViewTestMixin
from catwatch.tests.lib.assertions import assert_status_with_message
from catwatch.blueprints.issue.models import Issue


class TestSettings(ViewTestMixin):
    def test_support_page(self):
        """ Support page renders successfully. """
        response = self.client.get(url_for('issue.support'))

        assert response.status_code == 200

    def test_support_page_while_logged_in(self):
        """ Support page renders successfully with pre-populated e-mail. """
        self.login()
        response = self.client.get(url_for('issue.support'))

        assert_status_with_message(200, response,
                                   'value="admin@localhost.com"')

    def test_support(self):
        """ Support issue gets saved. """
        old_issue_count = Issue.query.count()
        issue = {
            'label': 'login',
            'email': 'foo@bar.com',
            'question': 'Help!'
        }

        response = self.client.post(url_for('issue.support'), data=issue,
                                    follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Help is on the way, expect a response '
                                     'shortly.'))

        new_issue_count = Issue.query.count()
        assert (old_issue_count + 1) == new_issue_count

    def test_support_invalid_label(self):
        """ Support issue fails due to an invalid label. """
        issue = {
            'label': 'notlegit',
            'email': 'foo@bar.com',
            'question': 'Help!'
        }

        response = self.client.post(url_for('issue.support'), data=issue,
                                    follow_redirects=True)

        assert_status_with_message(200, response, 'Not a valid choice')
