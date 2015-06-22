from flask import (
    Blueprint,
    flash,
    redirect,
    url_for,
    render_template)
from flask_login import current_user
from flask_babel import gettext as _

from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.issue.forms import SupportForm

issue = Blueprint('issue', __name__, template_folder='templates')


@issue.route('/support', methods=['GET', 'POST'])
def support():
    # Pre-populate the email field if the user is signed in.
    form = SupportForm(obj=current_user)

    if form.validate_on_submit():
        i = Issue()

        form.populate_obj(i)
        i.save()

        # This prevents circular imports.
        from catwatch.blueprints.issue.tasks import deliver_support_email

        deliver_support_email.delay(i.id)

        flash(_('Help is on the way, expect a response shortly.'), 'success')
        return redirect(url_for('issue.support'))

    return render_template('issue/support.jinja2', form=form)
