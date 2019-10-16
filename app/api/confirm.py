from flask_restplus import Namespace, Resource, fields
from app.models import User
from . import errors as err
from .models import error_fields

api = Namespace('confirm', description='confirmation email')


@api.route('/<string:token>')
class Confirm(Resource):
    """ todo """

    @api.response(200, 'OK')
    @api.response(400, 'Bad Request', error_fields)
    def get(self, token):
        """ Подтверждение email. """

        email = User.get_email_by_token(token)

        if not email:
            raise err.InvalidLincError()

        user = User.get_or_none(User.email == email)

        if not user:
            raise err.InvalidLincError()
        if user.confirmed:
            raise err.AlreadyConfirmedError()

        user.confirmed = True
        user.save()

        return {'message': 'Email confirmed.'}
