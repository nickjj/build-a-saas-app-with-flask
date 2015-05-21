from flask import url_for
from flask_babel import gettext as _

from catwatch.tests.lib.util import login, logout
from catwatch.tests.lib.assertions import assert_status_with_message
from catwatch.blueprints.user.models import User


class TestLogin:
    def test_login_page(self, session, client):
        """ Login page renders successfully. """
        response = client.get(url_for('user.login'))
        assert response.status_code == 200

    def test_login(self, session, client):
        """ Login successfully. """
        response = login(client, 'admin@localhost.com', 'password')
        assert response.status_code == 200

    def test_login_activity(self, session, client):
        """ Login successfully and update the activity stats. """
        user = User.find_by_identity('admin@localhost.com')
        old_sign_in_count = user.sign_in_count

        response = login(client, 'admin@localhost.com', 'password')

        new_sign_in_count = user.sign_in_count

        assert response.status_code == 200
        assert (old_sign_in_count + 1) == new_sign_in_count

    def test_login_disable(self, session, client):
        """ Login failure due to account being disabled. """
        response = login(client, 'disabled@localhost.com', 'password')

        assert_status_with_message(200, response,
                                   _('This account has been disabled.'))

    def test_login_fail(self, session, client):
        """ Login failure due to invalid login credentials. """
        response = login(client, 'foo@invalid.com', 'password')
        assert_status_with_message(200, response,
                                   _('Identity or password is incorrect.'))

    def test_logout(self, session, client):
        """ Logout successfully. """
        login(client, 'admin@localhost.com', 'password')

        response = logout(client)
        assert_status_with_message(200, response,
                                   _('You have been logged out.'))

    def test_logout_without_being_logged_in(self, session, client):
        """ Logout failure due to not being logged in. """
        response = logout(client)
        assert_status_with_message(200, response,
                                   'Please log in to access this page.')


class TestPasswordReset:
    def test_begin_password_reset_page(self, session, client):
        """ Begin password reset renders successfully. """
        response = client.get(url_for('user.begin_password_reset'))
        assert response.status_code == 200

    def test_password_reset_page(self, session, client):
        """ Password reset renders successfully. """
        response = client.get(url_for('user.password_reset'))
        assert response.status_code == 200

    def test_begin_password_reset_as_logged_in(self, session, client):
        """ Begin password reset should redirect to settings. """
        # login(client, 'admin@localhost.com', 'password')
        # response = client.get(url_for('user.begin_password_reset'),
        # follow_redirects=False)
        #
        # assert response.status_code == 302
        pass

    def test_password_reset_as_logged_in(self, session, client):
        """ Password reset should redirect to settings. """
        # login(client, 'admin@localhost.com', 'password')
        # response = client.get(url_for('user.password_reset'),
        #                       follow_redirects=False)
        #
        # assert response.status_code == 302
        pass

    def test_begin_password_reset_fail(self, session, client):
        """ Begin reset failure due to using a non-existent account. """
        user = {'identity': 'foo@invalid.com'}
        response = client.post(url_for('user.begin_password_reset'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response, 'Unable to locate account.')

    def test_begin_password_reset(self, session, client):
        """ Begin password reset successfully. """
        user = {'identity': 'admin@localhost.com'}
        response = client.post(url_for('user.begin_password_reset'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('An email has been sent to %(email)s.',
                                     email='admin@localhost.com'))

    def test_password_reset(self, session, client, token):
        """ Reset successful. """
        reset = {'password': 'newpassword', 'reset_token': token}
        response = client.post(url_for('user.password_reset'), data=reset,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Your password has been reset.'))

        admin = User.find_by_identity('admin@localhost.com')
        assert admin.password != 'newpassword'

    def test_password_reset_empty_token(self, session, client):
        """ Reset failure due to empty reset token. """
        reset = {'password': 'newpassword'}
        response = client.post(url_for('user.password_reset'), data=reset,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Your reset token has expired or was '
                                     'tampered with.'))

    def test_password_reset_invalid_token(self, session, client):
        """ Reset failure due to tampered reset token. """
        reset = {'password': 'newpassword', 'token': '123'}
        response = client.post(url_for('user.password_reset'), data=reset,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Your reset token has expired or was '
                                     'tampered with.'))


class TestSignup:
    def test_signup_page(self, session, client):
        """ Signup renders successfully. """
        response = client.get(url_for('user.signup'))

        assert response.status_code == 200

    def test_welcome_page(self, session, client):
        """ Welcome renders successfully. """
        login(client, 'admin@localhost.com', 'password')
        response = client.get(url_for('user.welcome'))

        assert response.status_code == 200

    def test_begin_signup_fail_logged_in(self, session, client):
        """ Signup should redirect to settings. """
        # login(client, 'admin@localhost.com', 'password')
        # response = client.get(url_for('user.signup'),
        # follow_redirects=False)
        #
        # assert response.status_code == 302
        pass

    def test_begin_signup_fail(self, session, client):
        """ Signup failure due to using an account that exists. """
        user = {'email': 'admin@localhost.com', 'password': 'password'}
        response = client.post(url_for('user.signup'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response, 'Already exists.')

    def test_signup(self, session, client):
        """ Signup successfully. """
        old_user_count = User.query.count()

        user = {'email': 'newperson@localhost.com', 'password': 'password'}
        response = client.post(url_for('user.signup'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Awesome, thanks for signing up!'))

        new_user_count = User.query.count()
        assert (old_user_count + 1) == new_user_count

        new_user = User.find_by_identity('newperson@localhost.com')
        assert new_user.password != 'password'

    def test_welcome(self, session, client):
        """ Create username successfully. """
        login(client, 'admin@localhost.com', 'password')

        user = {'username': 'hello'}
        response = client.post(url_for('user.welcome'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Sign up is complete, enjoy our '
                                     'services.'))

    def test_welcome_with_existing_username(self, session, client):
        """ Create username failure due to username already existing. """
        login(client, 'admin@localhost.com', 'password')

        u = User.find_by_identity('admin@localhost.com')
        u.username = 'hello'
        u.save()

        user = {'username': 'hello'}
        response = client.post(url_for('user.welcome'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response, 'Already exists.')


class TestSettings:
    def test_settings_page(self, session, client):
        """ Settings renders successfully. """
        login(client, 'admin@localhost.com', 'password')
        response = client.get(url_for('user.settings'))

        assert response.status_code == 200

    def test_settings_page_without_logged_in(self, session, client):
        """ Settings renders successfully. """
        response = client.get(url_for('user.settings'))

        assert_status_with_message(200, response,
                                   'Please log in to access this page.')


class TestUpdateCredentials:
    def test_update_credentials_page(self, session, client):
        """ Upate credentials renders successfully. """
        login(client, 'admin@localhost.com', 'password')
        response = client.get(url_for('user.update_credentials'))

        assert response.status_code == 200

    def test_update_credentials_page_without_logged_in(self, session, client):
        """ Update credentials renders successfully. """
        response = client.get(url_for('user.update_credentials'))

        assert_status_with_message(200, response,
                                   'Please log in to access this page.')

    def test_begin_update_credentials_invalid_current(self, session, client):
        """ Update credentials failure due to invalid current password. """
        login(client, 'admin@localhost.com', 'password')

        user = {'current_password': 'nope', 'email': 'admin@localhost.com'}
        response = client.post(url_for('user.update_credentials'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response, 'Does not match.')

    def test_begin_update_credentials_existing_email(self, session, client):
        """ Update credentials failure due to existing account w/ email. """
        login(client, 'admin@localhost.com', 'password')

        user = {
            'current_password': 'password',
            'email': 'disabled@localhost.com'
        }
        response = client.post(url_for('user.update_credentials'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response, 'Already exists.')

    def test_begin_update_credentials_email_change(self, session, client):
        """ Update credentials but only the e-mail address. """
        login(client, 'admin@localhost.com', 'password')

        user = {
            'current_password': 'password',
            'email': 'admin2@localhost.com'
        }
        response = client.post(url_for('user.update_credentials'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Your sign in settings have been '
                                     'updated.'))

        old_user = User.find_by_identity('admin@localhost.com')
        assert old_user is None

        new_user = User.find_by_identity('admin2@localhost.com')
        assert new_user is not None

    def test_begin_update_credentials_password_change(self, session, client):
        """ Update credentials but only the password. """
        login(client, 'admin@localhost.com', 'password')

        user = {
            'current_password': 'password',
            'email': 'admin@localhost.com',
            'password': 'newpassword'
        }

        response = client.post(url_for('user.update_credentials'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Your sign in settings have been '
                                     'updated.'))

        logout(client)
        login(client, 'admin@localhost.com', 'newpassword')
        assert response.status_code == 200

    def test_begin_update_credentials_email_password(self, session, client):
        """ Update both the email and a new password. """
        login(client, 'admin@localhost.com', 'password')

        user = {
            'current_password': 'password',
            'email': 'admin2@localhost.com',
            'password': 'newpassword'
        }
        response = client.post(url_for('user.update_credentials'), data=user,
                               follow_redirects=True)

        assert_status_with_message(200, response,
                                   _('Your sign in settings have been '
                                     'updated.'))
