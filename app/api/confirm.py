from flask_restplus import Namespace, Resource
from app.models import User

api = Namespace('confirm', description='description confirm namespace #todo')


@api.route('/<string:token>')
class Confirm(Resource):
    """ todo """

    def get(self, token):
        email = User.get_email_by_token(token)

        if not email:
            api.abort(400)
            # raise apiErr.InvalidLincError()

        user = User.get_or_none(User.email == email)

        if not user:
            api.abort(400)
            # raise apiErr.InvalidLincError()
        if user.confirmed:
            api.abort(400)
            # raise apiErr.AlreadyConfirmedError()

        user.confirmed = True
        user.save()

        return {'message': 'Email confirmed.'}
