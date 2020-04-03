from flask import Blueprint
 
home = Blueprint('home', __name__)
 
@home.route('/')
def hello():
    return 'Hello Flask!'
