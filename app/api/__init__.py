from flask import Blueprint
from flask_restplus import Api

from .users import api as users_api

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint,
          title='title first api',
          description='description first api')
# api = Api(
#     title='title first api',
#     description='description first api'
# )

api.add_namespace(users_api)