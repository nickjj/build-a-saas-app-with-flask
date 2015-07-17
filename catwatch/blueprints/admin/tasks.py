from catwatch.extensions import mail
from catwatch.app import create_celery_app
from catwatch.blueprints.issue.models import Issue

celery = create_celery_app()


@celery.task()
def deliver_support_email(issue_id, subject, message):
    """
    Send a contact message to the person who sent an issue.

    :param user_id: Id of the user
    :type user_id: int
    :param subject: E-mail subject
    :type subject: str
    :param message: E-mail message
    :type message: str
    :return: None
    """
    issue = Issue.query.get(issue_id)

    if issue is None:
        return

    mail.send_message(sender=celery.conf.get('MAIL_USERNAME'),
                      recipients=[issue.email],
                      reply_to=celery.conf.get('MAIL_USERNAME'),
                      subject=subject,
                      body=message)

    return None
