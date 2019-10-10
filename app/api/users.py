from flask_restplus import Namespace, Resource

api = Namespace('users', description='description users namespace')


@api.route('/')
class HelloWorld(Resource):
    def get(self):
        return 'Hello world.'


