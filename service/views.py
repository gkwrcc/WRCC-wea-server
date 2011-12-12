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
    from libwea.products.listers import test_list
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
    from libwea.products.listers import getData
    error = require(request, ['stn', 'sD', 'eD'])
    if error:
        return ErrorResponse(error)

    stn = request.args.get('stn')
    sD = parse_date(request.args.get('sD'))
    eD = parse_date(request.args.get('eD'))

    try:
        result = getData(stn, sD, eD)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)


@expose('/getDataSingleDay')
def getDataSingleDay(request):
    from libwea.products.listers import getDataSingleDay
    error = require(request, ['stn', 'sD'])
    if error:
        return ErrorResponse(error)

    stn = request.args.get('stn')
    sD = parse_date(request.args.get('sD'))

    try:
        result = getDataSingleDay(stn, sD)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)
