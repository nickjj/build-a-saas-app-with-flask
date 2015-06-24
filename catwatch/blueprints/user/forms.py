import logging

from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import EmailField, Unique, Email
from flask_babel import lazy_gettext as _

try:
    from instance import settings

    LANGUAGES = settings.LANGUAGES
except ImportError:
    logging.error('Ensure __init__.py and settings.py both exist in instance/')
    exit(1)
except AttributeError:
    from config import settings

    LANGUAGES = settings.LANGUAGES

from catwatch.lib.util_wtforms import ModelForm, choices_from_dict
from catwatch.blueprints.user.models import User, db
from catwatch.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class LoginForm(Form):
    next = HiddenField()
    identity = StringField(_('Username or email'),
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField(_('Stay signed in'))


class BeginPasswordResetForm(Form):
    identity = StringField(_('Username or email'),
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists]
                           )


class PasswordResetForm(Form):
    reset_token = HiddenField()
    password = PasswordField(_('Password'), [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField(_('Password'), [DataRequired(), Length(8, 128)])


class WelcomeForm(ModelForm):
    username_message = _('Letters, numbers and underscores only please.')

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])


class UpdateCredentials(ModelForm):
    email = EmailField(validators=[
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    current_password = PasswordField(_('Current password'),
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches]
                                     )
    password = PasswordField(_('Password'), [Optional(), Length(8, 128)])


class UpdateLocale(ModelForm):
    locale = SelectField(_('Language preference'), [DataRequired()],
                         choices=choices_from_dict(LANGUAGES))
