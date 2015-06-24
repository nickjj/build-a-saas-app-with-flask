import datetime

import pytz

from catwatch.lib.money import cents_to_dollars, dollars_to_cents
from catwatch.blueprints.billing.models.credit_card import CreditCard
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.models.invoice import Invoice


class TestMoney(object):
    def test_cents_convert_to_dollars(self):
        """ Cents become dollars. """
        assert cents_to_dollars(0) == 0.0
        assert cents_to_dollars(5) == 0.05
        assert cents_to_dollars(-20) == -0.2
        assert cents_to_dollars(100) == 1

    def test_cents_dollars_to_cents(self):
        """ Dollars become cents. """
        assert dollars_to_cents(2.33) == 233
        assert dollars_to_cents(-4) == -400
        assert dollars_to_cents(1) == 100
        assert dollars_to_cents(-0) == 0


class TestCreditCard(object):
    def test_credit_card_expiring_soon(self):
        """ Credit card is expiring soon. """
        may_29_2015 = datetime.date(2015, 05, 29)
        exp_dates = (
            datetime.date(2000, 1, 1),
            datetime.date(2015, 6, 3),
            datetime.date(2015, 7, 1)
        )

        for date in exp_dates:
            assert CreditCard.is_expiring_soon(may_29_2015, date)

    def test_credit_card_not_expiring_soon(self):
        """ Credit card is not expiring soon. """
        may_29_2015 = datetime.date(2015, 05, 29)
        exp_dates = (
            datetime.date(2015, 8, 28),
            datetime.date(2016, 1, 1),
            datetime.date(2016, 5, 29)
        )

        for date in exp_dates:
            assert CreditCard.is_expiring_soon(may_29_2015, date) is False

    def test_mark_old_credit_cards(self, session, credit_cards):
        """ Credit cards that are about to expire should get marked. """
        may_29_2015 = datetime.date(2015, 05, 29)
        june_29_2015 = datetime.date(2015, 06, 29)

        CreditCard.mark_old_credit_cards(may_29_2015)

        card = CreditCard.query.filter(CreditCard.exp_date == june_29_2015)
        assert True == card.first().is_expiring

    def test_avoid_marking_up_to_date_credit_cards(self, session,
                                                   credit_cards):
        """ Credit cards that are not expiring should not be marked. """
        may_29_2015 = datetime.date(2015, 05, 29)
        may_28_2016 = datetime.date(2016, 05, 28)

        CreditCard.mark_old_credit_cards(may_29_2015)

        card = CreditCard.query.filter(CreditCard.exp_date == may_28_2016)
        assert False == card.first().is_expiring


class TestCoupon(object):
    def test_random_coupon_code(self):
        """ Random coupon code is created. """
        from catwatch.blueprints.billing.tasks import expire_old_coupons

        expire_old_coupons.delay()

        random_coupon = Coupon.random_coupon_code()
        assert len(random_coupon) == 14
        assert random_coupon.isupper()

    def test_coupon_should_get_invalidated(self, session, coupons):
        """ Coupons that are not redeemable should expire. """
        may_29_2015 = datetime.datetime(2015, 05, 29, 0, 0, 0)
        may_29_2015 = pytz.utc.localize(may_29_2015)

        june_29_2015 = datetime.datetime(2015, 06, 29, 0, 0, 0)
        june_29_2015 = pytz.utc.localize(june_29_2015)

        Coupon.expire_old_coupons(june_29_2015)

        coupon = Coupon.query.filter(Coupon.redeem_by == may_29_2015)
        assert coupon.first().valid is False

    def test_coupon_should_not_get_invalidated(self, session, coupons):
        """ Coupons that haven't expired should remain valid. """
        may_29_2015 = datetime.datetime(2015, 05, 29, 0, 0, 0)
        may_29_2015 = pytz.utc.localize(may_29_2015)

        june_29_2015 = datetime.datetime(2015, 06, 29, 0, 0, 0)
        june_29_2015 = pytz.utc.localize(june_29_2015)

        Coupon.expire_old_coupons(may_29_2015)

        coupon = Coupon.query.filter(Coupon.redeem_by == june_29_2015)
        assert coupon.first().valid is True

    def test_coupon_without_redeem_by_should_be_valid(self, session, coupons):
        """ Coupons that do not expire should be valid. """
        Coupon.expire_old_coupons()

        coupon = Coupon.query.filter(Coupon.redeem_by.is_(None))
        assert coupon.first().valid is True


class TestInvoice(object):
    def test_parse_payload_from_event(self):
        """ Parse out the data correctly from a Stripe event paypload. """
        event_payload = {
            'created': 1326853478,
            'livemode': False,
            'id': 'evt_000',
            'type': 'invoice.created',
            'object': 'event',
            'request': None,
            'pending_webhooks': 1,
            'api_version': '2015-04-07',
            'data': {
                'object': {
                    'date': 1433018770,
                    'id': 'in_000',
                    'period_start': 1433018770,
                    'period_end': 1433018770,
                    'lines': {
                        'data': [
                            {
                                'id': 'sub_000',
                                'object': 'line_item',
                                'type': 'subscription',
                                'livemode': True,
                                'amount': 0,
                                'currency': 'usd',
                                'proration': False,
                                'period': {
                                    'start': 1433162255,
                                    'end': 1434371855
                                },
                                'subscription': None,
                                'quantity': 1,
                                'plan': {
                                    'interval': 'month',
                                    'name': 'Gold',
                                    'created': 1424879591,
                                    'amount': 500,
                                    'currency': 'usd',
                                    'id': 'gold',
                                    'object': 'plan',
                                    'livemode': False,
                                    'interval_count': 1,
                                    'trial_period_days': 14,
                                    'metadata': {},
                                    'statement_descriptor': 'GOLD MONTHLY'
                                },
                                'description': None,
                                'discountable': True,
                                'metadata': {}
                            }
                        ],
                        'total_count': 1,
                        'object': 'list',
                        'url': '/v1/invoices/in_000/lines'
                    },
                    'subtotal': 0,
                    'total': 500,
                    'customer': 'cus_000',
                    'object': 'invoice',
                    'attempted': False,
                    'closed': True,
                    'forgiven': False,
                    'paid': True,
                    'livemode': False,
                    'attempt_count': 0,
                    'amount_due': 0,
                    'currency': 'usd',
                    'starting_balance': 0,
                    'ending_balance': 0,
                    'next_payment_attempt': None,
                    'webhooks_delivered_at': None,
                    'charge': None,
                    'discount': None,
                    'application_fee': None,
                    'subscription': 'sub_000',
                    'tax_percent': None,
                    'tax': None,
                    'metadata': {},
                    'statement_descriptor': None,
                    'description': None,
                    'receipt_number': '0009000'
                }
            }
        }

        parsed_payload = Invoice.parse_from_event(event_payload)

        assert parsed_payload['payment_id'] == 'cus_000'
        assert parsed_payload['plan'] == 'Gold'
        assert parsed_payload['receipt_number'] == '0009000'
        assert parsed_payload['description'] == 'GOLD MONTHLY'
        assert parsed_payload['period_start_on'] == datetime.date(2015, 6, 1)
        assert parsed_payload['period_end_on'] == datetime.date(2015, 6, 15)
        assert parsed_payload['currency'] == 'usd'
        assert parsed_payload['tax'] is None
        assert parsed_payload['tax_percent'] is None
        assert parsed_payload['total'] == 500

    def test_invoice_upcoming(self, mock_stripe):
        """ Parse out the data correctly from a Stripe invoice payload. """
        parsed_payload = Invoice.upcoming('cus_000')

        next_bill_on = datetime.datetime(2015, 5, 30, 20, 46, 10)

        assert parsed_payload['plan'] == 'Gold'
        assert parsed_payload['description'] == 'GOLD MONTHLY'
        assert parsed_payload['next_bill_on'] == next_bill_on
        assert parsed_payload['amount_due'] == 500
        assert parsed_payload['interval'] == 'month'
