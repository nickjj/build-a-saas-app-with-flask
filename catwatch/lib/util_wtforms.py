from flask_wtf import Form
from flask_babel import lazy_gettext as _


class ModelForm(Form):
    """
    wtforms_components exposes ModelForm but their ModelForm does not inherit
    from flask_wtf's Form, but instead WTForm's Form.

    However, in order to get csrf protection handled by default we need to
    inherit from flask_wtf's Form. So let's just copy his class directly.

    We modified it by removing the format argument so that wtforms_component
    uses its own default which is to pass in request.form automatically.
    """

    def __init__(self, obj=None, prefix='', **kwargs):
        Form.__init__(
            self, obj=obj, prefix=prefix, **kwargs
        )
        self._obj = obj


def choices_from_dict(source, prepend_blank=True):
    """
    Convert a dict to a format that's compatible with WTForm's choices. It also
    optionally prepends a "Please select one..." value.

    Example:
      # Convert this data structure:
      STATUS = OrderedDict([
          ('unread', 'Unread'),
          ('open', 'Open'),
          ('contacted', 'Contacted'),
          ('closed', 'Closed')
      ])

      # Into this:
      choices = [('', 'Please select one...'), ('unread', 'Unread) ...]

    :param source: The dict as input
    :type source: dict
    :param prepend_blank: An optional blank item
    :type prepend_blank: bool
    :return: list
    """
    choices = []

    if prepend_blank:
        choices.append(('', _('Please select one...')))

    for key, value in source.iteritems():
        pair = (key, value)
        choices.append(pair)

    return choices
