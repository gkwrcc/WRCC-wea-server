# Library code for listing-type products.
# Functions should return dicts to be json-ized.

import os
import datetime
from libwea.wea_array import WeaArray
from libwea.wea_array import WeaFile
from libwea.meta import WeaMeta
from libwea.elements import WeaElements, DEFAULT_FORMAT
from libwea.utils import filename_from_yearmonth, \
    datetime_from_DAYTIM, get_var_units
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


def getData(stn, sD, eD, units_system='N'):
    """
    Get all elements for a stn in native time interval.
    """
    w = WeaArray(stn, sD, eD, units_system=units_system)
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
        'units': {},
        'elements': {},
    }

    for var in var_list:
        try:
            fmt = WeaElements[var]['format']
        except KeyError:
            fmt = DEFAULT_FORMAT
        # Populate formatted data
        data_list = list(w.get_var(var))
        for i in range(len(data_list)):
            if data_list[i] in settings.MISSINGS:
                data_list[i] = None
            else:
                data_list[i] = fmt % data_list[i]
        result['data'][var] = data_list
        # Populate units
        result['units'][var] = get_var_units(var, units_system=units_system)
        # Populate element names
        try:
            result['elements'][var] = WeaElements[var]['name']
        except KeyError:
            pass

    return result


def getDataSingleDay(stn, sD, units_system='N'):
    """
    Get all elements for a single day.
    """
    # First, calculate ending date
    sD = sD.replace(hour=0, minute=0)
    eD = sD.replace(hour=23, minute=59)

    return getData(stn, sD, eD, units_system=units_system)


def getMostRecentData(stn, eD=None, units_system='N'):
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
    latest_data = wea.latest_data()  # TODO: Convert data to units_system
    latest_data_dt = datetime_from_DAYTIM(latest_data["DAY"],
                        latest_data["TIM"])
    units = {}
    for pcode in latest_data:
        units[pcode] = get_var_units(pcode)
        #units[pcode] = get_var_units(pcode, units_system=units_system)  # conversions not yet implemented

    # Use this to return the common format?, but data
    # will be lists of 1 element, # and datafile is read twice.
    #return getData(stn, latest_data_dt, latest_data_dt)

    result = {
        'stn': stn,
        'oi': header['oi'],
        'rgt': header['rgt'],
        'fac1': header['fac1'],
        'fac2': header['fac2'],
        'eD': latest_data_dt.timetuple()[:5],
        'data': latest_data,
        'units': units
    }
    return result


if __name__ == '__main__':
    d = getMostRecentData('nnsc')
