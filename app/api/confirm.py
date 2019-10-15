from flask_restplus import Namespace, Resource
from app.models import User
import app.api.errors as err

api = Namespace('confirm', description='description confirm namespace #todo')


@api.route('/<string:token>')
class Confirm(Resource):
    """ todo """

    def get(self, token):
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
