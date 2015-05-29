import datetime


def timedelta_months(months, compare_date=None):
    """
    Return a JSON response.

    :param months: Amount of months to offset
    :type months: int
    :param compare_date: Date to compare at
    :type compare_date: date
    :return: Flask response
    """
    if compare_date is None:
        compare_date = datetime.date.today()

    delta = months * 365 / 12
    compare_date_with_delta = compare_date + datetime.timedelta(delta)

    return compare_date_with_delta
