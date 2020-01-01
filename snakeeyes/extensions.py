from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_static_digest import FlaskStaticDigest


debug_toolbar = DebugToolbarExtension()
mail = Mail()
csrf = CSRFProtect()
flask_static_digest = FlaskStaticDigest()
