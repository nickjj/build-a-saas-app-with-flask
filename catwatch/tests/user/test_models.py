from catwatch.blueprints.user.models import User


class TestLogin:
    def test_serialize_token(self, token):
        """ Token serializer serializes a JWS correctly. """
        assert token.count('.') == 2

    def test_deserialize_token(self, token):
        """ Token de-serializer de-serializes a JWS correctly. """
        user = User.deserialize_token(token)
        assert user.email == 'admin@localhost.com'

    def test_deserialize_token_tampered(self, token):
        """ Token deserializer returns None when it's been tampered with. """
        user = User.deserialize_token('{0}1337'.format(token))
        assert user is None
