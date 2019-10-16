from flask import g
from flask_restplus import Namespace, Resource, reqparse
from app.models import User as bdUser
from werkzeug.exceptions import BadRequest
from . import errors as err
from .logging import logging_request
from .auth import token_auth
from .models import user_fields, user_list_fields, token_field, error_fields


api = Namespace('users', description='database management')


@api.errorhandler(BadRequest)  # BadRequest # Exception
def api_error(error):

    # if hasattr(error, 'data') and 'errors' in error.data and (
    #     'username' in error.data['errors'] or
    #     'email' in error.data['errors'] or
    #     'password' in error.data['errors']
    # ):
    #     error.data = err.InsufficientDataError('Must include username, email and password fields.')

    error.data = err.InsufficientDataError('Must include username, email and password fields.')


add_parser = reqparse.RequestParser()
add_parser.add_argument('username', required=True, help='Username cannot be blank!')
add_parser.add_argument('email', required=True, help='Email cannot be blank!')
add_parser.add_argument('birthday')
add_parser.add_argument('password', required=True, help='Password cannot be blank!')

update_parser = reqparse.RequestParser()
update_parser.add_argument('username')
update_parser.add_argument('email')
update_parser.add_argument('birthday')
update_parser.add_argument('password')


@api.route('/')
class Users(Resource):
    """ todo """

    @token_auth.login_required
    @logging_request(logging=True)
    @api.response(401, 'Unauthorized ', error_fields)
    @api.response(404, 'Not Found', error_fields)
    @api.marshal_with(user_list_fields, description='OK')
    @api.doc(security='BearerAuth')
    def get(self):
        """ Возвращает коллекцию всех пользователей. """

        data = bdUser.select()
        if not data:  # в теории невозможно
            raise err.NotFoundError('Users not found.')

        return {'users': data}

    @logging_request(logging=True)
    @api.response(201, 'Created', token_field)
    @api.response(400, 'Bad Request', error_fields)
    @api.response(409, 'Conflict', error_fields)
    @api.doc(parser=add_parser)
    def post(self):
        """ Регистрирует новую учетную запись пользователя. """

        args = add_parser.parse_args()

        if bdUser.get_or_none(bdUser.username == args['username']):
            raise err.NameUsedError()

        if bdUser.get_or_none(bdUser.email == args['email']):
            raise err.EmailUsedError()

        user = bdUser()
        user.create_user(args)  # переписать имя метода
        user.save()

        token = user.generate_confirmation_token()

        return {'message': f'Link to confirm email: <domain>/api/confirm/{token}'}, 201


@api.route('/<int:id>')
@api.response(401, 'Unauthorized ', error_fields)
@api.response(403, 'Forbidden', error_fields)
@api.response(404, 'Not Found', error_fields)
@api.doc(security='BearerAuth', params={'id': 'An ID'})
class User(Resource):
    """ todo """

    @token_auth.login_required
    @logging_request(logging=True)
    @api.marshal_with(user_fields, description='OK')
    def get(self, id):
        """ Возвращает пользователя. """

        user = bdUser.get_or_none(bdUser.id == id)

        if not user:
            raise err.NotFoundError('User not found.')
        if g.current_user.get_id != user.get_id:
            raise err.RightsError()

        return user

    @token_auth.login_required
    @logging_request(logging=True)
    @api.response(409, 'Conflict', error_fields)
    @api.marshal_with(user_fields, description='OK')
    @api.doc(parser=update_parser)
    def put(self, id):
        """ Изменение пользователя. """

        user = bdUser.get_or_none(bdUser.id == id)
        if not user:
            raise err.NotFoundError('User not found.')
        if g.current_user.get_id != user.get_id:
            raise err.RightsError()

        args = update_parser.parse_args()

        if 'username' in args and args['username'] != user.username and \
                bdUser.get_or_none(bdUser.username == args['username']):
            raise err.NameUsedError()
        if 'email' in args and args['email'] != user.email and \
                bdUser.get_or_none(bdUser.email == args['email']):
            raise err.EmailUsedError()

        user.update_user(args)
        user.save()

        return user

# todo
# записать по типу в readme
# db.connect()
# db.create_tables([User])
