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

    def test_is_last_admin_yes(self, token):
        """ Last admin should not be able to demote himself. """
        assert True == User.is_last_admin('admin', 'member')
        assert False == User.is_last_admin('admin', 'admin')

    def test_is_last_admin_no(self, token):
        """ Not the last admin should be able to demote himself. """
        params = {
            'role': 'admin',
            'email': 'hello@world.com',
            'password': 'password'
        }

        new_user = User(**params)
        new_user.save()

        assert False == User.is_last_admin('admin', 'member')
