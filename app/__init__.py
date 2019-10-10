from flask import Flask
from .api import blueprint as api

app = Flask(__name__)
# api.init_app(app)
app.register_blueprint(api)
app.run(debug=True)
