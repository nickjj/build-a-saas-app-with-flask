from catwatch.app import create_celery_app
from catwatch.blueprints.billing.models.credit_card import CreditCard
from catwatch.blueprints.billing.models.coupon import Coupon

celery = create_celery_app()


@celery.task()
def mark_old_credit_cards():
    """
    Mark credit cards that are going to expire soon or have expired.

    :return: The result of updating the records
    """
    return CreditCard.mark_old_credit_cards()


@celery.task()
def expire_old_coupons():
    """
    Invalidate coupons that are past their redeem date.

    :return: The result of updating the records
    """
    return Coupon.expire_old_coupons()


@celery.task()
def delete_coupons(ids):
    """
    Delete coupons both on Stripe and locally.

    :param ids: List of ids to be deleted
    :type ids: list
    :return: The number of deleted coupons.
    """
    return Coupon.bulk_delete(ids)
