from flask import request
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer

from catwatch.extensions import login_manager, babel


def authentication(app, user_model):
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


def locale(app):
    """
    Initialize a locale for the current request.

    :param app: Flask application instance
    :return: str
    """
    @babel.localeselector
    def get_locale():
        if current_user.is_authenticated():
            return current_user.locale

        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)
