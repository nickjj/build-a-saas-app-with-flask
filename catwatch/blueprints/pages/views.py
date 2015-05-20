from flask import Blueprint, render_template


pages = Blueprint('pages', __name__, template_folder='templates')


@pages.route('/')
def home():
    return render_template('pages/home.jinja2')


@pages.route('/learn-more')
def learn_more():
    return render_template('pages/learn_more.jinja2')


@pages.route('/faq')
def faq():
    return render_template('pages/faq.jinja2')


@pages.route('/terms')
def terms():
    return render_template('pages/terms.jinja2')


@pages.route('/privacy')
def privacy():
    return render_template('pages/privacy.jinja2')
