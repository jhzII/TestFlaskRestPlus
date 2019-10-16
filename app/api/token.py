from flask import g
from flask_restplus import Namespace, Resource
from .auth import basic_auth, token_auth
from .errors import NotConfirmedError
from .models import token_field, error_fields

api = Namespace('token', description='authorization')


@api.route('')
class Token(Resource):
    """ todo """

    @basic_auth.login_required
    @api.response(200, 'OK', token_field)
    @api.response(400, 'Bad Request', error_fields)
    @api.doc(security='BasicAuth')
    def post(self):
        """
        Генерация токена доступа.

        Запросы по токену будут доступны час.
        """

        if not g.current_user.get_confirmed():
            token = g.current_user.generate_confirmation_token()
            raise NotConfirmedError('Email not confirmed. Link to confirm email: ' +
                                    f'<domen>/confirm/{token}')
        token = g.current_user.get_token()
        return {'token': token}

    @token_auth.login_required
    @api.doc(security='BearerAuth', responses={204: 'No Content'})
    def delete(self):
        """ Удалениие кода доступа. """
        g.current_user.revoke_token()
        return '', 204
