from flask_babel import lazy_gettext as _

from catwatch.lib.flask_mailplus import send_template_message
from catwatch.app import create_celery_app
from catwatch.blueprints.issue.models import Issue

celery = create_celery_app()


@celery.task()
def deliver_support_email(issue_id):
    """
    Send a support e-mail.

    :param user_id: Id of the user
    :type user_id: int
    :return: None
    """
    issue = Issue.query.get(issue_id)

    if issue is None:
        return

    ctx = {'issue': issue}

    send_template_message(subject=_('[Support request] %(label)s',
                                    label=issue.label),
                          sender=issue.email,
                          recipients=[celery.conf.get('MAIL_USERNAME')],
                          reply_to=issue.email,
                          template='issue/mail/support', ctx=ctx)

    return None
