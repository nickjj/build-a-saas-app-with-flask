from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template)
from flask_login import login_required, current_user
from flask_babel import ngettext as _n
from flask_babel import gettext as _
from sqlalchemy import text

from catwatch.blueprints.admin.models import Dashboard
from catwatch.blueprints.user.decorators import role_required
from catwatch.blueprints.user.models import User
from catwatch.blueprints.issue.models import Issue
from catwatch.blueprints.admin.forms import SearchForm, BulkDeleteForm, \
    UserForm, IssueForm


admin = Blueprint('admin', __name__,
                  template_folder='templates', url_prefix='/admin')


@admin.before_request
@login_required
@role_required('admin')
def before_request():
    """ We are protecting all of our admin endpoints. """
    pass


# Dashboard -------------------------------------------------------------------
@admin.route('')
def dashboard():
    group_and_count_users = Dashboard.group_and_count_users()
    group_and_count_issues = Dashboard.group_and_count_issues()

    return render_template('admin/pages/dashboard.jinja2',
                           group_and_count_users=group_and_count_users,
                           group_and_count_issues=group_and_count_issues)


# Users -----------------------------------------------------------------------
@admin.route('/users', defaults={'page': 1})
@admin.route('/users/page/<int:page>')
def users(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = User.sort_by(request.args.get('sort', 'name'),
                           request.args.get('direction', 'asc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_users = User.query \
        .filter(User.search(request.args.get('q', ''),
                            ('email', 'name'))) \
        .order_by(User.role.desc(), text(order_values)) \
        .paginate(page, 20, True)

    return render_template('admin/user/index.jinja2',
                           form=search_form, bulk_form=bulk_form,
                           users=paginated_users)


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def users_edit(id):
    user = User.query.get(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        if User.is_last_admin(user.role, request.form.get('role', None)):
            flash(_('You are the last admin, you cannot demote yourself.'),
                  'error')
            return redirect(url_for('admin.users'))

        form.populate_obj(user)

        if user.username == '':
            user.username = None
        user.save()

        flash(_('User has been saved successfully.'), 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user/edit.jinja2', form=form, user=user)


@admin.route('/users/bulk_delete', methods=['POST'])
def users_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = User.get_bulk_action_ids(request.form.get('scope', None),
                                       request.form.getlist('bulk_ids'),
                                       omit_ids=[current_user.id],
                                       query=request.args.get('q', ''),
                                       query_fields=('email', 'name'))

        delete_count = User.bulk_delete(ids)

        flash(_n('%(num)d user was deleted.',
                 '%(num)d users were deleted.',
                 num=delete_count), 'success')
    else:
        flash(_('No users were deleted, something went wrong.'), 'error')

    return redirect(url_for('admin.users'))


# Issues ----------------------------------------------------------------------
@admin.route('/issues', defaults={'page': 1})
@admin.route('/issues/page/<int:page>')
def issues(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Issue.sort_by(request.args.get('sort', 'status'),
                            request.args.get('direction', 'asc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_issues = Issue.query \
        .filter(Issue.search(request.args.get('q', ''), ('email'))) \
        .order_by(text(order_values)) \
        .paginate(page, 20, True)

    return render_template('admin/issue/index.jinja2',
                           form=search_form, bulk_form=bulk_form,
                           issues=paginated_issues, LABEL=Issue.LABEL)


@admin.route('/issues/edit/<int:id>', methods=['GET', 'POST'])
def issues_edit(id):
    issue = Issue.query.get(id)
    form = IssueForm(obj=issue)

    if form.validate_on_submit():
        form.populate_obj(issue)
        issue.save()

        flash(_('Issue has been saved successfully.'), 'success')
        return redirect(url_for('admin.issues'))

    return render_template('admin/issue/edit.jinja2', form=form, issue=issue)


@admin.route('/issues/bulk_delete', methods=['POST'])
def issues_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Issue.get_bulk_action_ids(request.form.get('scope', None),
                                        request.form.getlist('bulk_ids'),
                                        query=request.args.get('q', ''),
                                        query_fields=('email'))

        delete_count = Issue.bulk_delete(ids)

        flash(_n('%(num)d issue was deleted.',
                 '%(num)d issues were deleted.',
                 num=delete_count), 'success')
    else:
        flash(_('No issues were deleted, something went wrong.'), 'error')

    return redirect(url_for('admin.issues'))
