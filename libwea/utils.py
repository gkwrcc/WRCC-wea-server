#
# Common utility functions.
#

import re
import datetime
from elements import Conversions, WeaElements


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


def yearmonth_from_filename(filename):
    """
    Determine the year and month based on filename.
    """
    m = int(filename[-8:][:2])
    y = int(filename[-8:][2:4])

    if y < 40:
        y = int("20%02d" % y)
    else:
        y = int("19%02d" % y)
    return (y, m)


def filename_from_yearmonth(ym, stn_id):
    """
    Produce a .wea filename for the year/month tuple ym.
    """
    y4 = "%04d" % int(ym[0])
    y2 = y4[2:]
    m2 = "%02d" % int(ym[1])
    stn_id = str(stn_id).lower()
    return "%s%s%s.wea" % (stn_id, m2, y2)


def is_valid_filename(filename, stn_id):
    """
    Determine if the given filename is a valid wea data
    file for this stn_id.
    """
    #           stn   valid months                        year   .wea
    pattern = "^" + stn_id
    pattern += "(01|02|03|04|05|06|07|08|09|10|11|12)(\d\d)(\.wea)$"
    regex = re.compile(pattern)
    return bool(regex.match(filename))


def datetime_from_DAYTIM(DAY, TIM, year=None):
    """
    Return a datetime object equal to Julian day DAY
    and HHMM TIM.
    """
    if year is None:
        year = datetime.date.today().year  # noqa
    ret = datetime.datetime(year, 1, 1) + datetime.timedelta(int(DAY) - 1)
    HHMM = "%04d" % int(TIM)
    hour = int(HHMM[:2])
    minute = int(HHMM[2:])
    ret = ret.replace(hour=hour, minute=minute)
    return ret


def wea_convert(unit, units_system):
    """
    This function returns a tuple (func, units) where:
    - func is a function to convert the given unit to the given system
    - units is the units returned by func

    This only works with linear conversions.
    """
    if (unit, units_system) in Conversions:
        mult, offset, units2 = Conversions[(unit, units_system)]
        return (lambda x: (x*mult)+offset, units2)
    return (None,None)


def get_var_units(pcode, units_system='N'):
    """
    Return the units for the given pcode.
    """
    try:
        elem = WeaElements[pcode]
        if units_system == 'N':
            return elem["units"]
        conv_f, new_units = wea_convert(elem['units'], units_system)
        if new_units:
            return new_units
        return elem["units"]
    except KeyError:
        return None
