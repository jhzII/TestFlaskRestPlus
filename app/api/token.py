from flask_restplus import Namespace, Resource
from app.api.auth import basic_auth, token_auth
from flask import g

api = Namespace('token', description='description token namespace #todo')


@api.route('')
class Token(Resource):
    """ todo """

    @basic_auth.login_required
    def post(self):
        if not g.current_user.get_confirmed():
            token = g.current_user.generate_confirmation_token()
            return f'Link to confirm email: <domain>/api/confirm/{token}', 400
            # raise NotConfirmedError('Email not confirmed. Link to confirm email: ' +
            #                        f'<domen>/confirm/{token}')
        token = g.current_user.get_token()
        return {'token': token}

    @token_auth.login_required
    def delete(self):
        g.current_user.revoke_token()
        return '', 204
