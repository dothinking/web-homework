# app.py
from flask import Flask
from admin.views import admin
from home.views import home
 
app = Flask(__name__)
app.register_blueprint(home)
app.register_blueprint(admin, url_prefix='/admin')
