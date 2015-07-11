from flask import Blueprint, current_app, render_template, redirect, url_for
from flask_login import login_required, current_user

stream = Blueprint('stream', __name__, template_folder='templates')


@stream.route('/live_stream')
@login_required
def live_stream():
    if not current_user.subscription:
        return redirect(url_for('billing.pricing'))

    faye = {
        'public_url': current_app.config.get('BROADCAST_PUBLIC_URL')
    }

    return render_template('stream/live_stream.jinja2', faye=faye)
