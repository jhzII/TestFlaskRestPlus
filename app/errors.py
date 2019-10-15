from app import app
from flask import make_response, jsonify
from app.api.errors import ApiError


@app.errorhandler(Exception)
def api_error(error):
    if isinstance(error, ApiError):
        return error.make_response()

    if hasattr(error, 'data') and isinstance(error.data, ApiError):
        return error.data.make_response()

    return make_response(jsonify({
        'message': 'Internal error',
        'code': -1,
    }), 500)
