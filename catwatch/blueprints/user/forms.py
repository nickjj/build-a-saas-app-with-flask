from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import EmailField, Unique, Email
from flask_babel import lazy_gettext as _

from catwatch.blueprints.user.models import User, db
from catwatch.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class ModelForm(Form):
    """
    wtforms_components exposes ModelForm but their ModelForm does not inherit
    from flask_wtf's Form, but instead wtform's Form.

    However, in order to get csrf protection handled by default we need to
    inherit from flask_wtf's Form. So let's just copy his class directly.

    We modified it by removing the format argument so that wtforms_component
    uses its own default which is to pass in request.form automatically.
    """
    def __init__(self, obj=None, prefix='', **kwargs):
        Form.__init__(
            self, obj=obj, prefix=prefix, **kwargs
        )
        self._obj = obj


class LoginForm(Form):
    next = HiddenField()
    identity = StringField(_('Username or email'),
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField(_('Stay signed in'))
    submit = SubmitField(_('Sign in'))


class BeginPasswordResetForm(Form):
    identity = StringField(_('Username or email'),
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists]
                           )
    submit = SubmitField(_('Continue'))


class PasswordResetForm(Form):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    submit = SubmitField(_('Continue'))


class SignupForm(ModelForm):
    email = EmailField(validators=[
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField(_('Password'), [DataRequired(), Length(8, 128)])
    submit = SubmitField(_('Register'))


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
    submit = SubmitField(_('Save'))


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
    submit = SubmitField(_('Save'))
