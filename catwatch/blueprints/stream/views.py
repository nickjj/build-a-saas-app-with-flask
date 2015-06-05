from flask import Blueprint, current_app, render_template
from flask_login import login_required

stream = Blueprint('stream', __name__, template_folder='templates')


@stream.route('/live_stream')
@login_required
def live_stream():
    faye = {
        'public_url': current_app.config.get('BROADCAST_PUBLIC_URL')
    }

    return render_template('stream/live_stream.jinja2', faye=faye)
