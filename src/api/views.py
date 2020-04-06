from flask import Blueprint
 
api = Blueprint('api', __name__)
 
@api.route('/save_coordinate/')
def save_coordinate():
    return 'Hello save_coordinate!'

@api.route('/get_coordinates/')
def get_coordinates():
    return 'Hello get_coordinates!'
