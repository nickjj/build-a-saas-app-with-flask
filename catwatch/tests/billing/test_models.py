import datetime

from catwatch.lib.util_datetime import timedelta_months
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

    def test_mark_old_credit_cards(self, db):
        """ Credit cards that are about to expire should get marked. """
        may_29_2015 = datetime.date(2015, 05, 29)
        june_29_2015 = datetime.date(2015, 06, 29)

        params_expiring = {
            'user_id': 1,
            'brand': 'Visa',
            'last4': 4242,
            'exp_date': june_29_2015,
        }

        card = CreditCard(**params_expiring)

        db.session.add(card)
        db.session.commit()

        CreditCard.mark_old_credit_cards(may_29_2015)

        assert True == CreditCard.query.first().is_expiring

        db.session.delete(card)
        db.session.commit()

    def test_avoid_marking_old_credit_cards(self, db):
        """ Credit cards that are not expiring should not be marked. """
        may_29_2015 = datetime.date(2015, 05, 29)

        params_not_expiring = {
            'user_id': 1,
            'brand': 'Visa',
            'last4': 4242,
            'exp_date': timedelta_months(12, may_29_2015),
        }

        card = CreditCard(**params_not_expiring)

        db.session.add(card)
        db.session.commit()

        CreditCard.mark_old_credit_cards(may_29_2015)

        assert False == CreditCard.query.first().is_expiring

        db.session.delete(card)
        db.session.commit()


class TestCoupon:
    def test_random_coupon_code(self):
        """ Random coupon code is created. """
        from catwatch.blueprints.billing.tasks import expire_old_coupons

        expire_old_coupons.delay()

        random_coupon = Coupon.random_coupon_code()
        assert 14 == len(random_coupon)
        assert random_coupon.isupper()

    def test_coupon_should_get_invalidated(self, db):
        """ Coupons that are not redeemable should expire. """
        may_29_2015 = datetime.datetime(2015, 05, 29)
        june_29_2015 = datetime.datetime(2015, 06, 29)

        params_expiring = {
            'amount_off': 1,
            'redeem_by': may_29_2015
        }

        coupon = Coupon(**params_expiring)

        db.session.add(coupon)
        db.session.commit()

        Coupon.expire_old_coupons(june_29_2015)

        assert False == Coupon.query.first().valid

        db.session.delete(coupon)
        db.session.commit()

    def test_coupon_should_not_get_invalidated(self, db):
        """ Coupons that haven't expired should remain valid. """
        may_29_2015 = datetime.datetime(2015, 05, 29)
        june_29_2015 = datetime.datetime(2015, 06, 29)

        params_not_expiring = {
            'amount_off': 1,
            'redeem_by': june_29_2015
        }

        coupon = Coupon(**params_not_expiring)

        db.session.add(coupon)
        db.session.commit()

        Coupon.expire_old_coupons(may_29_2015)

        assert True == Coupon.query.first().valid

        db.session.delete(coupon)
        db.session.commit()

    def test_coupon_without_redeem_by_should_be_valid(self, db):
        """ Coupons that do not expire should be valid. """
        params_not_expiring = {
            'amount_off': 1,
        }

        coupon = Coupon(**params_not_expiring)

        db.session.add(coupon)
        db.session.commit()

        Coupon.expire_old_coupons()

        assert True == Coupon.query.first().valid

        db.session.delete(coupon)
        db.session.commit()
