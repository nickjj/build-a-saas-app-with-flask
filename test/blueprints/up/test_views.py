from flask import url_for


class TestUp(object):
    def test_up(self, client):
        """Up should respond with a success 200."""
        response = client.get(url_for("up.index"))
        assert response.status_code == 200

    def test_up_databases(self, client):
        """Up databases should respond with a success 200."""
        response = client.get(url_for("up.databases"))
        assert response.status_code == 200
