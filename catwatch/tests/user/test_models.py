from catwatch.blueprints.user.models import User


class TestUser(object):
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

    def test_is_last_admin_yes(self, users, token):
        """ Last admin should not be able to change himself. """
        user = User.find_by_identity('admin@localhost.com')

        assert User.is_last_admin(user, 'member', 'y') is True
        assert User.is_last_admin(user, 'admin', 'y') is False
        assert User.is_last_admin(user, 'admin', None) is True
        assert User.is_last_admin(user, 'member', None) is True

    def test_is_last_admin_no(self, users, token):
        """ Not the last admin should be able to change himself. """
        user = User.find_by_identity('admin@localhost.com')

        params = {
            'role': 'admin',
            'email': 'hello@world.com',
            'password': 'password'
        }

        new_user = User(**params)
        new_user.save()

        assert User.is_last_admin(user, 'member', 'y') is False
        assert User.is_last_admin(user, 'admin', None) is False
        assert User.is_last_admin(user, 'member', None) is False
