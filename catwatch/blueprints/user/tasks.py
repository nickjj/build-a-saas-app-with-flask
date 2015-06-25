from flask_babel import lazy_gettext as _

from catwatch.lib.flask_mailplus import send_template_message
from catwatch.app import create_celery_app
from catwatch.blueprints.user.models import User

celery = create_celery_app()


@celery.task()
def deliver_password_reset_email(user_id, reset_token):
    """
    Send a reset password e-mail to a user.

    :param user_id: The user id
    :type user_id: int
    :param reset_token: The reset token
    :type reset_token: str
    :return: None if a user was not found
    """
    user = User.query.get(user_id)

    if user is None:
        return

    ctx = {'user': user, 'reset_token': reset_token}

    send_template_message(subject=_('Password reset from Catwatch'),
                          recipients=[user.email],
                          template='user/mail/password_reset', ctx=ctx)

    return None
