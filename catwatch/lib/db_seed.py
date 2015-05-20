from catwatch.blueprints.user.models import User


def create_admin():
    """
    Create an admin account.

    :return: User instance
    """
    account_email = 'dev@localhost.com'

    if User.find_by_identity(account_email) is not None:
        return None

    params = {
        'role': 'admin',
        'email': account_email,
        'password': 'password'
    }

    return User(**params).save()


def seed_database():
    """
    Entry point to seed the database with whatever we see fit.

    :return: None
    """
    create_admin()
