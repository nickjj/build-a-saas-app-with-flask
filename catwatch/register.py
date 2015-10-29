import logging
import time
from logging.handlers import SMTPHandler

import stripe
from flask import g, request, render_template
from werkzeug.contrib.fixers import ProxyFix
from jinja2 import ChoiceLoader, FileSystemLoader

from catwatch.lib.http_method_override_middleware import \
    HTTPMethodOverrideMiddleware
from catwatch.blueprints.admin import admin
from catwatch.blueprints.page import page
from catwatch.blueprints.user import user
from catwatch.blueprints.issue import issue
from catwatch.blueprints.stream import stream
from catwatch.blueprints.billing.views.billing import billing
from catwatch.blueprints.billing.views.stripe_webhook import stripe_webhook
from catwatch.extensions import (
    db,
    bcrypt,
    mail,
    csrf,
    login_manager,
    bouncer,
    babel,
    cache,
    webpack,
    debug_toolbar
)
from catwatch.blueprints.billing.template_processors import format_currency

FLASK_BLUEPRINTS = [
    admin,
    page,
    user,
    issue,
    billing,
    stream,
    stripe_webhook
]

CUSTOM_ERROR_PAGES = [404, 500, 502]


def api_keys(app):
    """
    Register 0 or more API keys.

    :param app: Flask application instance
    :return: None
    """
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = app.config.get('STRIPE_API_VERSION')
    return None


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Allow modern HTTP verbs such as PATCH and DELETE.
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    return None


def blueprints(app):
    """
    Register 0 or more blueprints (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    for blueprint in FLASK_BLUEPRINTS:
        app.register_blueprint(blueprint)

    return None


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    bouncer.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    webpack.init_app(app)
    debug_toolbar.init_app(app)

    return None


def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    public_build_path = app.config.get('PUBLIC_BUILD_PATH')

    if public_build_path:
        multiple_template_loader = ChoiceLoader([
            app.jinja_loader,
            FileSystemLoader([public_build_path]),
        ])
        app.jinja_loader = multiple_template_loader

    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.filters['format_currency'] = format_currency

    return app.jinja_env


def logging_handler(app):
    """
    Register 0 or more logger handles (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    @app.before_request
    def before_request():
        """
        Save time when the request started.

        :return: None
        """
        g.start = time.time()

        return None

    @app.after_request
    def after_request(response):
        """
        Write out a log entry for the request.

        :return: Flask response
        """
        if 'start' in g:
            response_time = (time.time() - g.start)
        else:
            response_time = 0

        response_time_in_ms = int(response_time * 1000)

        params = {
            'method': request.method,
            'in': response_time_in_ms,
            'url': request.path,
            'ip': request.remote_addr
        }

        app.logger.info('%(method)s "%(url)s" in %(in)sms for %(ip)s', params)

        return response

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # This will not execute when debug is set to True.
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'),
                                app.config.get('MAIL_PORT')),
                               'bugs-noreply@catwatch.com',
                               [app.config.get('MAIL_USERNAME')],
                               '[Exception handler] A 5xx was thrown',
                               (app.config.get('MAIL_USERNAME'),
                                app.config.get('MAIL_PASSWORD')),
                               secure=())

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('''
    Time:         %(asctime)s
    Message type: %(levelname)s


    Message:

    %(message)s
    '''))
    app.logger.addHandler(mail_handler)

    return None


def error_templates(app):
    """
    Register 0 or more error handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        status_code = getattr(status, 'code', 500)
        return render_template('{0}.html'.format(status_code)), status_code

    for error in CUSTOM_ERROR_PAGES:
        app.errorhandler(error)(render_status)

    return None
