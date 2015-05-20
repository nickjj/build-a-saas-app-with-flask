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
from catwatch.blueprints.pages import pages
from catwatch.blueprints.user import user
from catwatch.blueprints.billing import billing
from catwatch.blueprints.issue import issue


def create_celery_app(app=None):
    """
    Create a new celery object and tie together the celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    task_list = [
        'catwatch.blueprints.user.tasks'
    ]

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=task_list)
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

    :param application_name: The name of the application
    :param settings_override: A dictionary of settings to override

    :return: Flask app
    """
    app = Flask(application_name, instance_relative_config=True)

    configure_settings(app, settings_override)
    register_middleware(app)
    register_blueprints(app)
    register_extensions(app)
    register_template_processors(app)
    initialize_authentication(app, User)
    initialize_locale(app)

    return app


def configure_settings(app, settings_override=None):
    """
    Create the settings of the application (mutates the app passed in).

    :param app: Flask application instance
    :param settings_override: A dictionary of settings to override

    :return: None
    """
    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)
    app.config.from_object(settings_override)


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


def register_blueprints(app):
    """
    Register 0 or more blueprints (mutates the app passed in).

    :param app: Flask application instance

    :return: None
    """
    blueprints = [
        pages,
        user,
        billing,
        issue
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


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


def register_template_processors(app):
    """
    Register 0 or more custom template filters (mutates the app passed in).

    :param app: Flask application instance

    :return: None
    """
    pass


def initialize_authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
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
    :return: None
    """
    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)
