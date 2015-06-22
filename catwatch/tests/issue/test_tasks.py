from catwatch.extensions import mail
from catwatch.blueprints.issue.tasks import deliver_support_email
from catwatch.blueprints.issue.models import Issue


class TestTasks(object):
    def test_deliver_support_email(self, issues):
        """ Deliver a support email. """
        with mail.record_messages() as outbox:
            issue = Issue.query.filter(Issue.email == 'admin@localhost.com') \
                .first()
            deliver_support_email(issue.id)

            assert len(outbox) == 1
            assert issue.email in outbox[0].body
