from catwatch.tests.lib.util import ViewTestMixin
from catwatch.tests.lib.assertions import assert_status_with_message


class TestErrorPages(ViewTestMixin):
    def test_404_page(self):
        """ 404 errors should show custom 404 page. """
        response = self.client.get('/impossiblepathtoneverexistinthisapp')

        assert_status_with_message(404, response, 'Error 404')
