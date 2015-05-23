from collections import OrderedDict

from flask_wtf import Form
from wtforms import SelectField, StringField, BooleanField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import Unique, EmailField
from flask_babel import lazy_gettext as _

from catwatch.lib.util_wtforms import choices_from_dict
from catwatch.blueprints.user.models import db, User
from catwatch.blueprints.issue.models import Issue


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


class SearchForm(Form):
    q = StringField(_('Search terms'), [Optional(), Length(1, 128)])
    submit = SubmitField(_('Search'))


class BulkDeleteForm(Form):
    SCOPE = OrderedDict([
        ('all_selected_products', 'All selected items'),
        ('all_search_results', 'All search results')
    ])

    scope = SelectField(_('Privileges'), [DataRequired()],
                        choices=choices_from_dict(SCOPE, prepend_blank=False))
    submit = SubmitField(_('Delete items'))


class UserForm(ModelForm):
    username_message = _('Letters, numbers and underscores only please.')

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        Optional(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])
    name = StringField(_('Full name'), [Optional(), Length(1, 128)])
    role = SelectField(_('Privileges'), [DataRequired()],
                       choices=choices_from_dict(User.ROLE,
                                                 prepend_blank=False))
    active = BooleanField(_('Yes, allow this user to sign in'))
    submit = SubmitField(_('Save'))


class IssueForm(Form):
    label = SelectField(_('What do you need help with?'), [DataRequired()],
                        choices=choices_from_dict(Issue.LABEL))
    email = EmailField(_("What's your e-mail address?"),
                       [DataRequired(), Length(3, 254)])
    question = TextAreaField(_("What's your question or issue?"),
                             [DataRequired(), Length(1, 8192)])
    status = SelectField(_('What status is the issue in?'), [DataRequired()],
                         choices=choices_from_dict(Issue.STATUS,
                                                   prepend_blank=False))
    submit = SubmitField(_('Save'))
