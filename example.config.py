import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
    SECURITY_PASSWORD_SALT = 'password_salt'
