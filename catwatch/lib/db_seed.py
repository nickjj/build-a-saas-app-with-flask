import logging

from catwatch.blueprints.user.models import User

try:
    from instance import settings

    SEED_ADMIN_EMAIL = settings.SEED_ADMIN_EMAIL
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    SEED_ADMIN_EMAIL = settings.SEED_ADMIN_EMAIL


def create_admin():
    """
    Create an admin account.

    :return: User instance
    """
    if User.find_by_identity(SEED_ADMIN_EMAIL) is not None:
        return None

    params = {
        'role': 'admin',
        'email': SEED_ADMIN_EMAIL,
        'password': 'password'
    }

    return User(**params).save()


def seed_database():
    """
    Entry point to seed the database with whatever we see fit.

    :return: None
    """
    create_admin()

    return None
