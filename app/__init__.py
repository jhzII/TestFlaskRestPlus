from flask import Flask
from config import Config
from peewee import SqliteDatabase

app = Flask(__name__)
app.config.from_object(Config)

db = SqliteDatabase('data.db')

from .api import logging  # уточнить способ
from .api import blueprint as api

app.register_blueprint(api)

from app import models, errors

app.run(debug=True)
