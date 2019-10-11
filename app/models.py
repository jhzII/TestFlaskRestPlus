# import os
# import base64
import peewee as pw
from app import app, db
# from datetime import datetime, timedelta
from itsdangerous import URLSafeSerializer, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash


class User(pw.Model):
    class Meta:
        database = db

    username = pw.CharField(64)
    email = pw.CharField(128)
    birthday = pw.DateField(formats='%Y-%m-%d', null=True)
    password_hash = pw.CharField(128)
    confirmed = pw.BooleanField(default=False)
    token = pw.CharField(32, index=True, unique=True, null=True)
    token_expiration = pw.DateField(formats='%Y-%m-%d %H:%M:%S', null=True)

    def create_user(self, data):
        for field in ['username', 'email', 'birthday']:
            if field in data:
                setattr(self, field, data[field])

        self.password_hash = generate_password_hash(data['password'])

    def update_user(self, data):
        for field in ['username', 'email', 'birthday']:
            if field in data:
                setattr(self, field, data[field])

        if 'password' in data:
            self.password_hash = generate_password_hash(data['password'])

    def get_user(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'birthday': self.birthday,
            'confirmed': self.confirmed
        }

    @staticmethod
    def get_all_users():
        return {
            'users': [{
                'id': user.id,
                'username': user.username,
                'birthday': user.birthday,
                'confirmed': user.confirmed
            } for user in User.select()]
        }

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_confirmed(self):
        return self.confirmed

    def generate_confirmation_token(self):
        serializer = URLSafeSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt=app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def get_email_by_token(token):
        serializer = URLSafeSerializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT']
            )
        except BadSignature:
            return None
        return email

    def __repr__(self):
        return f'<User {self.username}>'
