from flask_restplus import fields
from . import api


user_fields = api.model('User', {
    'id': fields.Integer(readonly=True, description='ID'),
    'username': fields.String(description='Имя пользователя.'),
    'email': fields.String(description='Email пользователя.'),
    'birthday': fields.String(description='Дата рождения.'),
    'confirmed': fields.String(readonly=True, description='Флаг подтверждения email.')
})

user_list_fields = api.model('Users', {
    'users': fields.List(fields.Nested(user_fields, skip_none=True, description='Список пользователей.'))
})

error_fields = api.model('Error', {
    'message': fields.String(description='Сообщение с описанием ошибки.'),
    'code': fields.Integer(description='Внутренний код ошибки.')
})

token_field = api.model('Token', {
    'message': fields.String(description='Сообщение с токеном.')
})
