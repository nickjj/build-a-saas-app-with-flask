from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf import CsrfProtect
from flask_login import LoginManager
from flask_bouncer import Bouncer
from flask_babel import Babel
from flask_cache import Cache
from flask_webpack import Webpack
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
csrf = CsrfProtect()
login_manager = LoginManager()
bouncer = Bouncer()
babel = Babel()
cache = Cache()
celery = Celery()
webpack = Webpack()
debug_toolbar = DebugToolbarExtension()
