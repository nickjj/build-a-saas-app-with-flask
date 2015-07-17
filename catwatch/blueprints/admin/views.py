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
from catwatch.blueprints.billing.decorators import handle_stripe_exceptions
from catwatch.blueprints.billing.models.coupon import Coupon
from catwatch.blueprints.billing.models.subscription import Subscription
from catwatch.blueprints.admin.forms import SearchForm, BulkDeleteForm, \
    UserForm, UserCancelSubscriptionForm, IssueForm, IssueContactForm, \
    CouponForm

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
    group_and_count_plans = Dashboard.group_and_count_plans()
    group_and_count_coupons = Dashboard.group_and_count_coupons()
    group_and_count_users = Dashboard.group_and_count_users()
    group_and_count_issues = Dashboard.group_and_count_issues()

    return render_template('admin/page/dashboard.jinja2',
                           group_and_count_plans=group_and_count_plans,
                           group_and_count_coupons=group_and_count_coupons,
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
        .filter(User.search(request.args.get('q', ''))) \
        .order_by(User.role.desc(), User.payment_id,
                  text(order_values)) \
        .paginate(page, 20, True)

    return render_template('admin/user/index.jinja2',
                           form=search_form, bulk_form=bulk_form,
                           users=paginated_users)


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def users_edit(id):
    user = User.query.get(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        if User.is_last_admin(user,
                              request.form.get('role'),
                              request.form.get('active')):
            flash(_('You are the last admin, you cannot do that.'),
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
        ids = User.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       omit_ids=[current_user.id],
                                       query=request.args.get('q', ''))

        # Prevent circular imports.
        from catwatch.blueprints.billing.tasks import delete_users

        delete_users.delay(ids)

        flash(_n('%(num)d user was scheduled to be deleted.',
                 '%(num)d users were scheduled to be deleted.',
                 num=len(ids)), 'success')
    else:
        flash(_('No users were deleted, something went wrong.'), 'error')

    return redirect(url_for('admin.users'))


@admin.route('/users/cancel_subscription', methods=['POST'])
def users_cancel_subscription():
    form = UserCancelSubscriptionForm()

    if form.validate_on_submit():
        user = User.query.get(request.form.get('id'))

        if user:
            subscription = Subscription()
            if subscription.cancel(user):
                flash(_('Subscription has been cancelled for %(user)s.',
                        user=user.name), 'success')
        else:
            flash(_('No subscription was cancelled, something went wrong.'),
                  'error')

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
        .filter(Issue.search(request.args.get('q', ''))) \
        .order_by(text(order_values)) \
        .paginate(page, 20, True)

    return render_template('admin/issue/index.jinja2',
                           form=search_form, bulk_form=bulk_form,
                           issues=paginated_issues, LABEL=Issue.LABEL)


@admin.route('/issues/edit/<int:id>', methods=['GET', 'POST'])
def issues_edit(id):
    issue = Issue.query.get(id)

    if request.method == 'GET' and issue and issue.status == 'unread':
        issue = Issue.unread_to_open(issue)

    form = IssueForm(obj=issue)

    subject = _('[Catwatch issue] Re: %(issue_type)s',
                issue_type=issue.LABEL[issue.label])

    # Shenanigans to comply with PEP-8's formatting style.
    body_string = '\n\nYou opened an issue regarding:'
    issue_string = '\n\n---\n{0}\n---\n\n'.format(issue.question)
    message = _('Hello,%(body)s:%(issue)s\n\nThanks,\nCatwatch support team',
                body=body_string, issue=issue_string)

    contact_form = IssueContactForm(email=issue.email,
                                    subject=subject, message=message)

    if form.validate_on_submit():
        form.populate_obj(issue)
        issue.save()

        flash(_('Issue has been saved successfully.'), 'success')
        return redirect(url_for('admin.issues'))

    return render_template('admin/issue/edit.jinja2', form=form,
                           contact_form=contact_form, issue=issue)


@admin.route('/issues/bulk_delete', methods=['POST'])
def issues_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Issue.get_bulk_action_ids(request.form.get('scope'),
                                        request.form.getlist('bulk_ids'),
                                        query=request.args.get('q', ''))

        delete_count = Issue.bulk_delete(ids)

        flash(_n('%(num)d issue was deleted.',
                 '%(num)d issues were deleted.',
                 num=delete_count), 'success')
    else:
        flash(_('No issues were deleted, something went wrong.'), 'error')

    return redirect(url_for('admin.issues'))


@admin.route('/issues/contact/<int:id>', methods=['POST'])
def issues_contact(id):
    issue = Issue.query.get(id)

    if issue:
        from catwatch.blueprints.admin.tasks import deliver_support_email
        deliver_support_email.delay(id,
                                    request.form.get('subject'),
                                    request.form.get('message'))

        Issue.set_as_contacted(issue)

        flash(_('The person who sent the issue has been contacted.'),
              'success')
    else:
        flash(_('Issue no longer exists, no e-mail was sent.'), 'error')

    return redirect(url_for('admin.issues'))


# Coupons ---------------------------------------------------------------------
@admin.route('/coupons', defaults={'page': 1})
@admin.route('/coupons/page/<int:page>')
def coupons(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Coupon.sort_by(request.args.get('sort', 'created_on'),
                             request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_coupons = Coupon.query \
        .filter(Coupon.search(request.args.get('q', ''))) \
        .order_by(text(order_values)) \
        .paginate(page, 20, True)

    return render_template('admin/coupon/index.jinja2',
                           form=search_form, bulk_form=bulk_form,
                           coupons=paginated_coupons)


@admin.route('/coupons/new', methods=['GET', 'POST'])
@handle_stripe_exceptions
def coupons_new():
    coupon = Coupon()
    form = CouponForm(obj=coupon)

    if form.validate_on_submit():
        form.populate_obj(coupon)

        params = {
            'code': coupon.code,
            'duration': coupon.duration,
            'percent_off': coupon.percent_off,
            'amount_off': coupon.amount_off,
            'currency': coupon.currency,
            'redeem_by': coupon.redeem_by,
            'max_redemptions': coupon.max_redemptions,
            'duration_in_months': coupon.duration_in_months,
        }

        if Coupon.create(params):
            flash(_('Coupon has been created successfully.'), 'success')
            return redirect(url_for('admin.coupons'))

    return render_template('admin/coupon/new.jinja2', form=form, coupon=coupon)


@admin.route('/coupons/bulk_delete', methods=['POST'])
@handle_stripe_exceptions
def coupons_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Coupon.get_bulk_action_ids(request.form.get('scope'),
                                         request.form.getlist('bulk_ids'),
                                         query=request.args.get('q', ''))

        # Prevent circular imports.
        from catwatch.blueprints.billing.tasks import delete_coupons

        delete_coupons.delay(ids)

        flash(_n('%(num)d coupon was scheduled to be deleted.',
                 '%(num)d coupons were scheduled to be deleted.',
                 num=len(ids)), 'success')
    else:
        flash(_('No coupons were deleted, something went wrong.'), 'error')

    return redirect(url_for('admin.coupons'))
