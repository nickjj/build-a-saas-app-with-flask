from flask_wtf import Form
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from flask_babel import lazy_gettext as _


class CreditCardForm(Form):
    stripe_key = HiddenField(_('Stripe key'),
                             [DataRequired(), Length(1, 254)])
    plan = HiddenField(_('Plan'),
                       [DataRequired(), Length(1, 254)])
    coupon_code = StringField(_('Do you have a discount code?'),
                              [Optional(), Length(1, 254)])
    name = StringField(_('Name on card'),
                       [DataRequired(), Length(1, 254)])
    submit = SubmitField(_('Process payment'))


class UpdateSubscriptionForm(Form):
    coupon_code = StringField(_('Do you have a discount code?'),
                              [Optional(), Length(1, 254)])
    submit = SubmitField(_('Change plan'))


class CancelSubscriptionForm(Form):
    submit = SubmitField(_('Cancel it'))
