import datetime

from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.extensions import db
from catwatch.blueprints.billing.services import StripeInvoice


class Invoice(ResourceMixin, db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='SET NULL'),
                        index=True, nullable=False)

    # Invoice details.
    plan = db.Column(db.String(128), index=True)
    receipt_number = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    period_start_on = db.Column(db.Date)
    period_end_on = db.Column(db.Date)
    currency = db.Column(db.String(8))
    tax = db.Column(db.Integer())
    tax_percent = db.Column(db.Float())
    total = db.Column(db.Integer())

    # De-normalize the card details so we can render a user's history properly
    # even if they have no active subscription or changed cards at some point.
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Invoice, self).__init__(**kwargs)

    @classmethod
    def upcoming(cls, customer_id):
        """
        Return the upcoming invoice item.

        :return: Stripe invoice object
        """
        stripe_invoice = StripeInvoice.upcoming(customer_id)
        plan_info = stripe_invoice['lines']['data'][0]['plan']
        date = datetime.datetime.utcfromtimestamp(stripe_invoice['date'])

        invoice = {
            'plan_name': plan_info['name'],
            'description': plan_info['statement_descriptor'],
            'next_bill_on': date.strftime('%B %d, %Y'),
            'amount_due': stripe_invoice['amount_due'],
            'interval': plan_info['interval']
        }

        return invoice
