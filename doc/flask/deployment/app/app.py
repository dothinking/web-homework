# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello Flask!'

@app.route('/admin/')
def admin_hello():
    return 'Hello Flask Admin!'