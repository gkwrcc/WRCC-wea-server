# Library code for listing-type products.
# Functions should return dicts to be json-ized.

import os
from libwea.wea_array import WeaArray
from libwea.wea_array import WeaFile
from libwea.meta import WeaMeta
from libwea.utils import filename_from_yearmonth
import settings


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


def getMostRecentData(stn, eD=None):
    """
    Get all elements for the most recent day of data,
    using eD as the last year/month to search.
    """
    stn_meta = WeaMeta(stn)
    if eD is None:
        eD = stn_meta.get_latest_month()
    # This may need another level of abstraction?
    fn = filename_from_yearmonth((eD.year, eD.month), stn)
    wea = WeaFile(os.path.join(settings.DATAPATH, stn, fn))

    header = wea.header

    result = {
        'stn': stn,
        'oi': header['oi'],
        'rgt': header['rgt'],
        'fac1': header['fac1'],
        'fac2': header['fac2'],
        'eD': eD.timetuple()[:5],
        'data': wea.latest_data(),
    }
    return result


if __name__ == '__main__':
    d = getMostRecentData('nnsc')
