import stripe
from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
from itsdangerous import URLSafeTimedSerializer
from celery import Celery

from catwatch.lib.http_method_override_middleware import \
    HTTPMethodOverrideMiddleware
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
from catwatch.blueprints.user.models import User
from catwatch.blueprints.admin import admin
from catwatch.blueprints.page import page
from catwatch.blueprints.user import user
from catwatch.blueprints.issue import issue
from catwatch.blueprints.stream import stream
from catwatch.blueprints.billing.views.billing import billing
from catwatch.blueprints.billing.views.stripe_webhook import stripe_webhook
from catwatch.blueprints.billing.template_processors import format_currency


CELERY_TASK_LIST = [
    'catwatch.blueprints.user.tasks',
    'catwatch.blueprints.issue.tasks',
    'catwatch.blueprints.billing.tasks',
    'catwatch.blueprints.stream.tasks',
]

FLASK_BLUEPRINTS = [
    admin,
    page,
    user,
    issue,
    billing,
    stream,
    stripe_webhook
]


def create_celery_app(app=None):
    """
    Create a new celery object and tie together the celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(application_name=__name__, settings_override=None):
    """
    Create an application using the Flask app factory pattern:
    http://flask.pocoo.org/docs/0.10/patterns/appfactories

    :param application_name: Name of the application
    :param settings_override: Override settings
    :type settings_override: dict
    :return: Flask app
    """
    app = Flask(application_name, instance_relative_config=True)

    configure_settings(app, settings_override)
    register_api_keys(app)
    register_middleware(app)
    register_blueprints(app)
    register_extensions(app)
    register_template_processors(app)
    initialize_authentication(app, User)
    initialize_locale(app)

    return app


def configure_settings(app, settings_override=None):
    """
    Modify the settings of the application (mutates the app passed in).

    :param app: Flask application instance
    :param settings_override: Override settings
    :type settings_override: dict
    :return: Add configuration settings
    """
    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    return app.config


def register_api_keys(app):
    """
    Register 0 or more API keys.

    :param app: Flask application instance
    :return: None
    """
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY', None)
    return None


def register_middleware(app):
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


def register_blueprints(app):
    """
    Register 0 or more blueprints (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    for blueprint in FLASK_BLUEPRINTS:
        app.register_blueprint(blueprint)

    return None


def register_extensions(app):
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


def register_template_processors(app):
    """
    Register 0 or more custom template filters (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.filters['format_currency'] = format_currency

    return app.jinja_env


def initialize_authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)

    @login_manager.token_loader
    def load_token(token):
        duration = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
        serializer = URLSafeTimedSerializer(app.secret_key)

        data = serializer.loads(token, max_age=duration)
        user_uid = data[0]

        return user_model.query.get(user_uid)


def initialize_locale(app):
    """
    Initialize a locale for the current request.

    :param app: Flask application instance
    :return: Language
    """
    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)
