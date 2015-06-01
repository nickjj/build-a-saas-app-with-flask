import datetime

from catwatch.blueprints.billing.models.credit_card import CreditCard, Money
from catwatch.blueprints.billing.models.coupon import Coupon


class TestMoney(object):
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
        may_29_2015 = datetime.date(2015, 05, 29)
        june_29_2015 = datetime.datetime(2015, 06, 29)

        Coupon.expire_old_coupons(june_29_2015)

        coupon = Coupon.query.filter(Coupon.redeem_by == may_29_2015)
        assert coupon.first().valid is False

    def test_coupon_should_not_get_invalidated(self, session, coupons):
        """ Coupons that haven't expired should remain valid. """
        may_29_2015 = datetime.datetime(2015, 05, 29)
        june_29_2015 = datetime.datetime(2015, 06, 29)

        Coupon.expire_old_coupons(may_29_2015)

        coupon = Coupon.query.filter(Coupon.redeem_by == june_29_2015)
        assert coupon.first().valid is True

    def test_coupon_without_redeem_by_should_be_valid(self, session, coupons):
        """ Coupons that do not expire should be valid. """
        Coupon.expire_old_coupons()

        coupon = Coupon.query.filter(Coupon.redeem_by.is_(None))
        assert coupon.first().valid is True
