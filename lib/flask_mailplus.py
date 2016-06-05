from flask import render_template

from snakeeyes.extensions import mail


def send_template_message(template=None, ctx=None, *args, **kwargs):
    """
    Send a templated e-mail using a similar signature as Flask-Mail:
    http://pythonhosted.org/Flask-Mail/

    Except, it also supports template rendering. If you want to use a template
    then just omit the body and html kwargs to Flask-Mail and instead supply
    a path to a template. It will auto-lookup and render text/html messages.

    Example:
        ctx = {'user': current_user, 'reset_token': token}
        send_template_message('Password reset from Foo', ['you@example.com'],
                              template='user/mail/password_reset', ctx=ctx)

    :param subject:
    :param recipients:
    :param body:
    :param html:
    :param sender:
    :param cc:
    :param bcc:
    :param attachments:
    :param reply_to:
    :param date:
    :param charset:
    :param extra_headers:
    :param mail_options:
    :param rcpt_options:
    :param template: Path to a template without the extension
    :param context: Dictionary of anything you want in the template context
    :return: None
    """
    if ctx is None:
        ctx = {}

    if template is not None:
        if 'body' in kwargs:
            raise Exception('You cannot have both a template and body arg.')
        elif 'html' in kwargs:
            raise Exception('You cannot have both a template and body arg.')

        kwargs['body'] = _try_renderer_template(template, **ctx)
        kwargs['html'] = _try_renderer_template(template, ext='html', **ctx)

    mail.send_message(*args, **kwargs)

    return None


def _try_renderer_template(template_path, ext='txt', **kwargs):
    """
    Attempt to render a template. We use a try/catch here to avoid having to
    do a path exists based on a relative path to the template.

    :param template_path: Template path
    :type template_path: str
    :param ext: File extension
    :type ext: str
    :return: str
    """
    try:
        return render_template('{0}.{1}'.format(template_path, ext), **kwargs)
    except IOError:
        pass
