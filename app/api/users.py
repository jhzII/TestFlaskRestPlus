from flask_restplus import Namespace, Resource, reqparse, fields
from app.models import User as bdUser
from flask import g

api = Namespace('users', description='description users namespace #todo')

# обработка на повторение
# написать ответ по модели
# документация методов
# настроить g

user_fields = api.model('User', {
    'id': fields.Integer(readonly=True),
    'username': fields.String,
    'email': fields.String,
    'birthday': fields.String,
    'confirmed': fields.String(readonly=True)
})

user_list_fields = api.model('Users', {
    'users': fields.List(fields.Nested(user_fields, skip_none=True))
})

add_parser = reqparse.RequestParser()
add_parser.add_argument('username', required=True, help='Not username.')  # , description='Имя пользователя.'
add_parser.add_argument('email', required=True, help='Not email.')  # , description='Email.')
add_parser.add_argument('birthday')  # , description='Дата рождения.')  # дата вроде строкой передается (уточнить)
add_parser.add_argument('password', required=True, help='Not password.')  # , description='Пароль.')

update_parser = reqparse.RequestParser()
update_parser.add_argument('username')
update_parser.add_argument('email')
update_parser.add_argument('birthday')
update_parser.add_argument('password')


@api.route('/')
class Users(Resource):
    """ todo """

    @api.marshal_with(user_list_fields)  # , description='Возвращает коллекцию всех пользователей.'
    def get(self):
        """ Возвращает коллекцию всех пользователей. """

        data = bdUser.select()
        if not data:  # в теории невозможно
            api.abort(404)
            # raise apiErr.NotFoundError('Users not found.')

        return {'users': data}

    @api.doc(parser=add_parser)
    def post(self):
        """ Регистрирует новую учетную запись пользователя. """

        args = add_parser.parse_args()

        if bdUser.get_or_none(bdUser.username == args['username']):
            api.abort(409)
            # raise apiErr.NameUsedError()

        if bdUser.get_or_none(bdUser.email == args['email']):
            api.abort(409)
            # raise apiErr.EmailUsedError()

        user = bdUser()
        user.create_user(args)  # переписать имя метода
        user.save()

        token = user.generate_confirmation_token()

        return {'message': f'Link to confirm email: <domain>/api/confirm/{token}'}


@api.route('/<int:id>')
class User(Resource):
    """ todo """

    @api.marshal_with(user_fields)
    def get(self, id):
        """ Возвращает пользователя. """

        user = bdUser.get_or_none(bdUser.id == id)

        if not user:
            api.abort(404)
            # raise apiErr.NotFoundError('User not found.')
        # if g.current_user.get_id != user.get_id:
        #     api.abort(401)
            # raise apiErr.RightsError()

        return user

    @api.doc(parser=update_parser)
    @api.marshal_with(user_fields)
    def put(self, id):
        """ Изменение пользователя. """

        user = bdUser.get_or_none(bdUser.id == id)
        if not user:
            api.abort(404)
            # raise apiErr.NotFoundError('User not found.')
        # if g.current_user.get_id != user.get_id:
        #     api.abort(401)
            # raise apiErr.RightsError()

        args = update_parser.parse_args()

        if 'username' in args and args['username'] != user.username and \
                bdUser.get_or_none(bdUser.username == args['username']):
            api.abort(409)
            # raise apiErr.NameUsedError()
        if 'email' in args and args['email'] != user.email and \
                bdUser.get_or_none(bdUser.email == args['email']):
            api.abort(409)
            # raise apiErr.EmailUsedError()

        user.update_user(args)
        user.save()

        return user


# записать по типу в readme
# db.connect()
# db.create_tables([User])
