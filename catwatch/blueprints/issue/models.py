from collections import OrderedDict

from sqlalchemy import or_

from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.extensions import db


class Issue(ResourceMixin, db.Model):
    STATUS = OrderedDict([
        ('unread', 'Unread'),
        ('open', 'Open'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed')
    ])

    LABEL = OrderedDict([
        ('login', 'I cannot access my account'),
        ('signup', 'I have a question before I sign up'),
        ('billing', 'I have a billing question'),
        ('email', 'I am not receiving e-mails'),
        ('request', 'I want to request a feature'),
        ('other', 'Other')
    ])

    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.Enum(*STATUS.keys(), name='status_types'),
                       index=True, nullable=False, server_default='unread')
    label = db.Column(db.Enum(*LABEL.keys(), name='label_types'),
                      index=True, nullable=False, server_default='login')
    email = db.Column(db.String(255), index=True, nullable=False,
                      server_default='')
    question = db.Column(db.Text())

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)

        return or_(Issue.email.ilike(search_query))

    @classmethod
    def unread_to_open(cls, issue):
        """
        Change unread issues to open.

        :param issue: Issue instance
        :type issue: Issue instance
        :return: Issue instance
        """
        issue.status = 'open'
        issue.save()

        return issue

    @classmethod
    def set_as_contacted(cls, issue):
        """
        Change an unknown issue type to contacted.

        :param issue: Issue instance
        :type issue: Issue instance
        :return: Issue instance
        """
        issue.status = 'contacted'
        issue.save()

        return issue
