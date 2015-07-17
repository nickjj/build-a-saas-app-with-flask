import logging
from collections import OrderedDict

from flask_wtf import Form
from wtforms import SelectField, StringField, BooleanField, TextAreaField, \
    FloatField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional, Regexp, \
    NumberRange
from wtforms_components import Unique, EmailField, IntegerField
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

from catwatch.lib.locale import Currency
from catwatch.lib.util_wtforms import ModelForm, choices_from_dict
from catwatch.blueprints.user.models import db, User
from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.billing.models.coupon import Coupon


class SearchForm(Form):
    q = StringField(_('Search terms'), [Optional(), Length(1, 128)])


class BulkDeleteForm(Form):
    SCOPE = OrderedDict([
        ('all_selected_products', 'All selected items'),
        ('all_search_results', 'All search results')
    ])

    scope = SelectField(_('Privileges'), [DataRequired()],
                        choices=choices_from_dict(SCOPE, prepend_blank=False))


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
    locale = SelectField(_('Language preference'), [DataRequired()],
                         choices=choices_from_dict(LANGUAGES))


class UserCancelSubscriptionForm(Form):
    pass


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


class IssueContactForm(Form):
    subject = StringField(_('Subject'), [DataRequired(), Length(1, 254)])
    message = TextAreaField(_('Message to be sent'),
                            [DataRequired(), Length(1, 8192)])


class CouponForm(Form):
    percent_off = IntegerField(_('Percent off'), [Optional(),
                                                  NumberRange(min=1, max=100)])
    amount_off = FloatField(_('Amount off'), [Optional(),
                                              NumberRange(min=0.01,
                                                          max=21474836.47)])
    code = StringField(_('Code'), [DataRequired(), Length(1, 32)])
    currency = SelectField(_('Currency'), [DataRequired()],
                           choices=choices_from_dict(Currency.TYPES,
                                                     prepend_blank=False))
    duration = SelectField(_('Duration'), [DataRequired()],
                           choices=choices_from_dict(Coupon.DURATION,
                                                     prepend_blank=False))
    duration_in_months = IntegerField(_('Duration in months'), [Optional(),
                                                                NumberRange(
                                                                    min=1,
                                                                    max=12)])
    max_redemptions = IntegerField(_('Max Redemptions'),
                                   [Optional(),
                                    NumberRange(min=1)])
    redeem_by = DateTimeField(_('Redeem by'), [Optional()],
                              format='%Y-%m-%d %H:%M:%S')

    def validate(self):
        if not Form.validate(self):
            return False

        result = True
        percent_off = self.percent_off.data
        amount_off = self.amount_off.data

        if percent_off is None and amount_off is None:
            self.percent_off.errors.append(_('Pick at least one.'))
            self.amount_off.errors.append(_('Pick at least one.'))
            result = False
        elif percent_off and amount_off:
            self.percent_off.errors.append(_('Cannot pick both.'))
            self.amount_off.errors.append(_('Cannot pick both.'))
            result = False
        else:
            result = True

        return result
