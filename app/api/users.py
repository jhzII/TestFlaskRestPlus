from flask_restplus import Namespace, Resource
from app.models import User

api = Namespace('users', description='description users namespace')


# @api.route('/')
# class HelloWorld(Resource):
#     def get(self):
#         return 'Hello world.'


@api.route('/')
class Users(Resource):
    def get(self):
        return User.get_all_users()

# записать по типу в readme
# db.connect()
# db.create_tables([User])