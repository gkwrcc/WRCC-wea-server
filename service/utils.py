import json
import datetime
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

# The global url map for this app.
url_map = Map([])


def expose(rule, **kw):
    """Used to decorate a view function."""
    def decorate(f):
        kw['endpoint'] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate


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
