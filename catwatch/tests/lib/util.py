from flask import url_for


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
