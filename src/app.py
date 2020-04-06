# app.py
from flask import Flask
from api.views import api

# flask app
app = Flask(__name__)

# blueprints
app.register_blueprint(api, url_prefix='/api')