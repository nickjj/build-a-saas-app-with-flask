from flask import Blueprint, render_template

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
def home():
    return render_template('page/home.jinja2')


@page.route('/learn-more')
def learn_more():
    return render_template('page/learn_more.jinja2')


@page.route('/faq')
def faq():
    return render_template('page/faq.jinja2')


@page.route('/terms')
def terms():
    return render_template('page/terms.jinja2')


@page.route('/privacy')
def privacy():
    return render_template('page/privacy.jinja2')
