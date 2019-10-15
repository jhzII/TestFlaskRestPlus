from app import app
from flask import request, g
from functools import wraps
from logging import FileHandler, Formatter, INFO


file_handler = FileHandler('logs/app.log')
file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s'))
app.logger.setLevel(INFO)
file_handler.setLevel(INFO)
app.logger.addHandler(file_handler)


def logging_request(logging=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if logging and not app.config['TESTING']:
                app.logger.info({'request': request.get_json() or {}})
                app.logger.info({
                    'user_id': g.current_user.id if 'current_user' in g and g.current_user else None
                })

            response = func(*args, **kwargs)

            if logging and not app.config['TESTING']:
                app.logger.info({'response': response or {}})

            return response
        return wrapper
    return decorator
