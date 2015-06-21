from werkzeug.urls import url_decode


class HTTPMethodOverrideMiddleware(object):
    """
    Allow us to route requests with modern HTTP verbs because browsers only
    currently support GET and POST. This is useful if you want to create a
    proper restful API.

    Source: http://flask.pocoo.org/docs/0.10/patterns/methodoverrides/

    Modified to also accept a query string __method__ as a source of truth:
      <form action="?__method__=DELETE">
    """
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS'
    ])

    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = self._detect_method(environ.get('QUERY_STRING', ''),
                                     environ.get('HTTP_X_HTTP_METHOD_OVERRIDE',
                                                 ''))

        if method in self.allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method

        if method in self.bodyless_methods:
            environ['CONTENT_LENGTH'] = '0'

        return self.app(environ, start_response)

    def _detect_method(self, query_string, method_override):
        """
        Determine the true method by investigating both the query string
        and the http method override header.

        :param query_string: Query string
        :type query_string: str
        :param method_override: Method override header
        :type method_override: str
        :return: str
        """
        if '__method__' in query_string:
            args = url_decode(query_string)
            method = args.get('__method__').upper()
        else:
            method = method_override.upper()

        return method
