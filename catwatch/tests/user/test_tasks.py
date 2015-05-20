from catwatch.extensions import mail
from catwatch.blueprints.user.tasks import deliver_password_reset_email


class TestTasks:
    def test_deliver_password_reset_email(self, token):
        """ Deliver a password reset email. """
        with mail.record_messages() as outbox:
            deliver_password_reset_email(1, token)

            assert len(outbox) == 1
            assert token in outbox[0].body
