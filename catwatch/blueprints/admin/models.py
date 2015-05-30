from sqlalchemy import func

from catwatch.blueprints.user.models import db, User
from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.billing.models.subscription import Subscription


class Dashboard(object):
    @classmethod
    def group_and_count_plans(cls):
        """
        Perform a group by/count on all subscriber types.

        :return: List of results
        """
        count = func.count(Subscription.plan)
        return db.session.query(count, Subscription.plan).group_by(
            Subscription.plan).all()

    @classmethod
    def group_and_count_coupons(cls):
        """
        Obtain coupon usage statistics across all subscribers.

        :return: Coupon stats
        """
        not_null = db.session.query(Subscription).filter(
            Subscription.coupon.isnot(None)).count()
        total = db.session.query(func.count(Subscription.id)).scalar()

        if total == 0:
            percent = 0
        else:
            percent = round((not_null / float(total)) * 100, 1)

        return not_null, total, percent

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
        Perform a group by/count on all issue types.

        :return: List of results
        """
        count = func.count(Issue.status)
        return db.session.query(count, Issue.status).group_by(
            Issue.status).all()
