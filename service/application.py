import os
import sys
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound

import views
from utils import url_map, ErrorResponse


class BaseApp(object):

    def __init__(self, config):
        self.config = config

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        adapter = url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(views, endpoint)
            response = handler(request, **values)
        except NotFound, e:
            response = ErrorResponse("URL Not Found")
            response.status_code = 404
        #except:
        #    response = ErrorResponse("Internal Server Error")
        #    response.status_code = 500

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app():
    app = BaseApp({})
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('0.0.0.0', 8000, app, use_debugger=True, use_reloader=True)
