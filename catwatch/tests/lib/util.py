import pytest
from flask import url_for


class ViewTestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(self, identity='admin@localhost.com', password='password'):
        """
        Login a specific user.

        Return: Flask response
        """
        return login(self.client, identity, password)

    def logout(self):
        """
        Login a specific user.

        Return: Flask response
        """
        return logout(self.client)


def login(client, username='', password=''):
    """
    Log a specific user in.

    :param client: Flask client
    :param username: The username
    :type username: str
    :param password: The password
    :type password: str
    :return: Flask response
    """
    user = dict(identity=username, password=password)
    response = client.post(url_for('user.login'), data=user,
                           follow_redirects=True)

    return response


def logout(client):
    """
    Log a specific user out.

    :param client: Flask client
    :return: Flask response
    """
    return client.get(url_for('user.logout'), follow_redirects=True)
