from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_static_digest import FlaskStaticDigest
from redis import Redis

from config.settings import REDIS_URL


debug_toolbar = DebugToolbarExtension()
mail = Mail()
csrf = CSRFProtect()
flask_static_digest = FlaskStaticDigest()
redis = Redis.from_url(REDIS_URL)
