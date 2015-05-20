def choices_from_dict(source, prepend_blank=True):
    """
    Convert a dict to a format that's compatible with WTForm's choices. It also
    optionally prepends a "Please select one..." value.

    Example:
      # Convert this data structure into:
      STATUS = OrderedDict([
          ('unread', 'Unread'),
          ('open', 'Open'),
          ('contacted', 'Contacted'),
          ('closed', 'Closed')
      ])

      # This:
      choices = [('', 'Please select one...'), ('unread', 'Unread) ...]

    :param source: The dict as input
    :type source: dict
    :param prepend_blank: An optional blank item
    :type prepend_blank: bool
    :return: List
    """
    choices = []

    if prepend_blank:
        choices.append(('', 'Please select one...'))

    for key, value in source.iteritems():
        pair = (key, value)
        choices.append(pair)

    return choices
