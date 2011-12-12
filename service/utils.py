import json
import datetime
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

# The global url map for this app.
url_map = Map([])


def expose(rule, **kw):
    """Expose a view function at the given URL."""
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate


def require(request, required_args):
    """Return error message if required_args aren't in request."""
    failed = []
    for arg in required_args:
        if request.args.get(arg, None) is None:
            failed.append(arg)
    if failed:
        return "Arguments required: %s" % ",".join(failed)


def JsonResponse(o):
    return Response(json.dumps(o), mimetype="application/json")


def ErrorResponse(s):
    return JsonResponse({"error": s})


def parse_date(date_string, sep="-"):
    """
    Parse a datetime object from request string.
    Date should be formatted YYYY-MM-DD-HH-MM.
    """
    if date_string is None:
        return None
    try:
        date_tuple = map(int, date_string.split(sep))
        dt = datetime.datetime(*date_tuple)
    except:
        return None
    return dt
