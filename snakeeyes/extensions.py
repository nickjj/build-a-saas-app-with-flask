from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_wtf import CSRFProtect

debug_toolbar = DebugToolbarExtension()
mail = Mail()
csrf = CSRFProtect()
