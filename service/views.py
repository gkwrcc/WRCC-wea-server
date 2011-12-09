# The view functions here are the bridge between http-aware code and
# backend library code.

import datetime
from utils import url_map, expose, \
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


@expose('/all_native')
def all_native(request):
    from libwea.products.listers import all_native
    stn = request.args.get('stn', None)
    if stn is None:
        return ErrorResponse("'stn' argument required.")
    sD = parse_date(request.args.get('sD', None))
    if sD is None:
        return ErrorResponse("'sD' argument required.")
    eD = parse_date(request.args.get('eD', None))
    if eD is None:
        return ErrorResponse("'eD' argument required.")

    try:
        result = all_native(stn, sD, eD)
    except IOError:
        return ErrorResponse("No data available.")

    return JsonResponse(result)
