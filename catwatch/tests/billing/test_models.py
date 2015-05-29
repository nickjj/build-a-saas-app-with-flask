import datetime

from catwatch.blueprints.billing.models.credit_card import CreditCard, Money
from catwatch.blueprints.billing.models.coupon import Coupon


class TestMoney:
    def test_cents_convert_to_dollars(self):
        """ Cents become dollars. """
        assert Money.cents_to_dollars(0) == 0.0
        assert Money.cents_to_dollars(5) == 0.05
        assert Money.cents_to_dollars(-20) == -0.2
        assert Money.cents_to_dollars(100) == 1

    def test_cents_dollars_to_cents(self):
        """ Dollars become cents. """
        assert Money.dollars_to_cents(2.33) == 233
        assert Money.dollars_to_cents(-4) == -400
        assert Money.dollars_to_cents(1) == 100
        assert Money.dollars_to_cents(-0) == 0


class TestCreditCard:
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
