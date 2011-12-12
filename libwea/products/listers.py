# Library code for listing-type products.
# Functions should return dicts to be json-ized.

from libwea.wea_array import WeaArray


def test_list(stn, sD, eD, var_list=None):
    w = WeaArray(stn, sD, eD)
    header = w.weafiles[-1].header
    if var_list is None:
        var_list = header['pcodes']

    result = {
        'stn': stn,
        'oi': header['oi'],
        'rgt': header['rgt'],
        'fac1': header['fac1'],
        'fac2': header['fac2'],
        'sD': sD.timetuple()[:5],
        'eD': eD.timetuple()[:5],
        'data': {},
    }

    for var in var_list:
        result['data'][var] = tuple(w.get_var(var))

    return result


def getData(stn, sD, eD):
    """
    Get all elements for a stn in native time interval.
    """
    w = WeaArray(stn, sD, eD)
    header = w.weafiles[-1].header
    var_list = header['pcodes']

    result = {
        'stn': stn,
        'oi': header['oi'],
        'rgt': header['rgt'],
        'fac1': header['fac1'],
        'fac2': header['fac2'],
        'sD': sD.timetuple()[:5],
        'eD': eD.timetuple()[:5],
        'data': {},
    }

    for var in var_list:
        result['data'][var] = tuple(w.get_var(var))

    return result


def getDataSingleDay(stn, sD):
    """
    Get all elements for a single day.
    """
    # First, calculate ending date
    sD = sD.replace(hour=0, minute=0)
    eD = sD.replace(hour=23, minute=59)

    return getData(stn, sD, eD)
