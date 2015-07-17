from flask import Flask
from celery import Celery

from catwatch.blueprints.user.models import User
from catwatch.register import (
    api_keys,
    blueprints,
    error_templates,
    exception_handler,
    extensions,
    logging_handler,
    middleware,
    template_processors
)
from catwatch.initialize import authentication, locale

CELERY_TASK_LIST = [
    'catwatch.blueprints.user.tasks',
    'catwatch.blueprints.issue.tasks',
    'catwatch.blueprints.billing.tasks',
    'catwatch.blueprints.stream.tasks',
    'catwatch.blueprints.admin.tasks',
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

    # Register.
    api_keys(app)
    middleware(app)
    blueprints(app)
    extensions(app)
    template_processors(app)
    logging_handler(app)
    exception_handler(app)
    error_templates(app)

    # Initialize.
    authentication(app, User)
    locale(app)

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
