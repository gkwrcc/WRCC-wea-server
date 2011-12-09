#
# Common utility functions.
#

import datetime


def round_date(d, mins, up=False):
    """
    Given a date, d, round it to the nearest minutes, mins.
    """
    ret = datetime.datetime(d.year, d.month, d.day, d.hour)
    if up:
        offset = datetime.timedelta(
            seconds=60 * ((d.minute - d.minute % mins) + mins)
        )
        return ret + offset
    else:
        offset = datetime.timedelta(seconds=60 * (d.minute - d.minute % mins))
        return ret + offset


def minutes_diff(sD, eD):
    """
    The number of minutes between sD and eD.
    """
    diff = eD - sD
    return 24 * 60 * diff.days + diff.seconds / 60


def days_in_month(mon, year):
    """
    Return the number of days in mon in given year.
    """
    m = int(mon)
    y = int(year)

    if m == 2:
        if is_leap(y):
            return 29
        else:
            return 28

    if m in (1, 3, 5, 7, 8, 10, 12):
        return 31

    if m in (4, 6, 9, 11):
        return 30

    raise ValueError(
        "Error calculating days in month: %s year: %s" % (mon, year)
    )


def is_leap(year):
    """
    Returns True if the given year is a leap year.
    """
    year = int(year)
    return bool(
        ((year % 4) == 0) and ((year % 100) != 0) or ((year % 400) == 0)
    )


def get_next_month(date):
    """
    Return a date object for the first day of
    the next month after the given date
    """
    if date.month == 12:
        return date.replace(year=date.year + 1, month=1, day=1)
    else:
        return date.replace(month=date.month + 1, day=1)
