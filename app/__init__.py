from flask import Flask
from config import Config
from .api import blueprint as api

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(api)

app.run(debug=True)
