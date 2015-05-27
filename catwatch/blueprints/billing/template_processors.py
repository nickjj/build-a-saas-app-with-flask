from catwatch.blueprints.billing.models.credit_card import Money


def format_currency(amount, cents_to_dollars=True):
    """
    Pad currency with 2 decimals and commas,
    optionally convert cents to dollars.

    :param amount: Amount in cents or dollars
    :type amount: int or float
    :return: str
    """
    if cents_to_dollars:
        amount = Money.cents_to_dollars(amount)

    return '{:,.2f}'.format(amount)
