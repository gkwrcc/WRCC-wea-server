# The view functions here are the bridge between http-aware code and
# backend library code.

import datetime
from utils import url_map, expose, require, \
            JsonResponse, ErrorResponse, \
            parse_date


@expose('/')
def list_routes(request):
    return JsonResponse({
        'routes': [(str(m.rule), m.endpoint)
            for m in url_map.iter_rules() if m.rule != '/']
    })


@expose('/test')
def test_list(request):
    "An example view"
    from wrcc.wea_server.libwea.products.listers import test_list
    stn = request.args.get('stn', None)
    if stn is None:
        return ErrorResponse("'stn' argument required.")
    sD = datetime.datetime(2011, 12, 7, 14)
    eD = datetime.datetime(2011, 12, 7, 15)
    try:
        result = test_list(stn, sD, eD)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)


@expose('/getData')
def getData(request):
    from wrcc.wea_server.libwea.products.listers import getData
    error = require(request, ['stn', 'sD', 'eD'])
    if error:
        return ErrorResponse(error)

    stn = request.args.get('stn')
    sD = parse_date(request.args.get('sD'))
    eD = parse_date(request.args.get('eD'))
    units_system = request.args.get('units', 'N')  # N (native) units by default

    try:
        result = getData(stn, sD, eD, units_system=units_system)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)


@expose('/getDataSingleDay')
def getDataSingleDay(request):
    from wrcc.wea_server.libwea.products.listers import getDataSingleDay
    error = require(request, ['stn', 'sD'])
    if error:
        return ErrorResponse(error)

    stn = request.args.get('stn')
    sD = parse_date(request.args.get('sD'))
    units_system = request.args.get('units', 'N')  # N (native) units by default

    try:
        result = getDataSingleDay(stn, sD, units_system=units_system)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)


@expose('/getMostRecentData')
def getMostRecentData(request):
    from wrcc.wea_server.libwea.products.listers import getMostRecentData
    error = require(request, ['stn'])
    if error:
        return ErrorResponse(error)

    stn = request.args.get('stn')
    eD = parse_date(request.args.get('eD', None))
    units_system = request.args.get('units', 'N')  # N (native) units by default

    try:
        result = getMostRecentData(stn, eD, units_system=units_system)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)


@expose('/getStnDates')
def getStnDates(request):
    from wrcc.wea_server.libwea.products.listers import getStnDates
    error = require(request, ['stn'])
    if error:
        return ErrorResponse(error)

    stn = request.args.get('stn')

    try:
        result = getStnDates(stn)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)
