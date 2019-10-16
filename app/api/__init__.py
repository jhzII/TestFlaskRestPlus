from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api', __name__, url_prefix='/api')

authorizations = {
    'BearerAuth': {     # Example: "Bearer <token>"
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
    'BasicAuth': {     # Example: "Basic <username>:<password>" #.encode()
        'type': 'basic'
    },
}

api = Api(blueprint,
          title='api service',
          description='api service using flask-restplus',
          authorizations=authorizations)

from .users import api as users_api
from .confirm import api as confirm_api
from .token import api as token_api

api.add_namespace(users_api)
api.add_namespace(confirm_api)
api.add_namespace(token_api)
