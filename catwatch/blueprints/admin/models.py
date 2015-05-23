from sqlalchemy import func

from catwatch.blueprints.user.models import db, User
from catwatch.blueprints.issue.models import Issue


class Dashboard(object):
    @classmethod
    def group_and_count_users(cls):
        """
        Perform a group by/count on all user types.

        :return: List of results
        """
        count = func.count(User.role)
        return db.session.query(count, User.role).group_by(User.role).all()

    @classmethod
    def group_and_count_issues(cls):
        """
        Perform a group by/count on all user types.

        :return: List of results
        """
        count = func.count(Issue.status)
        return db.session.query(count, Issue.status).group_by(
            Issue.status).all()
