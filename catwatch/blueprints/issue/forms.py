from flask_wtf import Form
from wtforms import TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms_components import EmailField
from flask_babel import lazy_gettext as _

from catwatch.lib.util_wtforms import choices_from_dict
from catwatch.blueprints.issue.models import Issue


class SupportForm(Form):
    label = SelectField(_('What do you need help with?'), [DataRequired()],
                        choices=choices_from_dict(Issue.LABEL))
    email = EmailField(_("What's your e-mail address?"),
                       [DataRequired(), Length(3, 254)])
    question = TextAreaField(_("What's your question or issue?"),
                             [DataRequired(), Length(1, 8192)])
