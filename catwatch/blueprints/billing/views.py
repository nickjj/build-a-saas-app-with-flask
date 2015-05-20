from flask import Blueprint, render_template


billing = Blueprint('billing', __name__, template_folder='templates')


@billing.route('/pricing')
def pricing():
    return render_template('billing/pricing.jinja2')
