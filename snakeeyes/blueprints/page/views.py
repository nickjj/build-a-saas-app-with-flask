from flask import Blueprint, render_template

from snakeeyes.extensions import redis


page = Blueprint('page', __name__, template_folder='templates')


@page.get('/')
def home():
    return render_template('page/home.html')


@page.get('/terms')
def terms():
    return render_template('page/terms.html')


@page.get('/privacy')
def privacy():
    return render_template('page/privacy.html')


@page.get('/up')
def up():
    redis.ping()
    return ''
