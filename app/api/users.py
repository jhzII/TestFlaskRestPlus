from flask_restplus import Namespace, Resource, reqparse, fields
from app.models import User as bdUser

api = Namespace('users', description='description users namespace TEST')

# обработка на повторение
# написать ответ по модели
# документация методов


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
    @api.marshal_with(user_list_fields)  # , description='Возвращает коллекцию всех пользователей.'
    def get(self):
        """ Возвращает коллекцию всех пользователей. """

        data = bdUser.select()
        if not data:  # в теории невозможно
            api.abort(404)
            # raise apiErr.NotFoundError('Users not found.')

        return {'users': data}

    @api.doc(parser=add_parser)
    @api.marshal_with(user_fields)
    def post(self):
        """ Регистрация нового пользователя. """

        args = add_parser.parse_args()
        # проверки на аргументы
        user = bdUser()
        user.create_user(args)  # переписать имя метода
        user.save()

        return user


@api.route('/<int:id>')
class User(Resource):
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

        args = update_parser.parse_args()

        user = bdUser.get_or_none(bdUser.id == id)
        if not user:
            api.abort(404)

        user.update_user(args)
        user.save()

        return user


# записать по типу в readme
# db.connect()
# db.create_tables([User])
