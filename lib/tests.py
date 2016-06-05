def assert_status_with_message(status_code=200, response=None, message=None):
    """
    Check to see if a message is contained within a response.

    :param status_code: Status code that defaults to 200
    :type status_code: int
    :param response: Flask response
    :type response: str
    :param message: String to check for
    :type message: str
    :return: None
    """
    assert response.status_code == status_code
    assert message in str(response.data)
