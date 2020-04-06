from flask import Blueprint, request, jsonify
import logging

api = Blueprint('api', __name__)
 
@api.route('/save_coordinate/', methods=['POST'])
def save_coordinate():
    json_data = request.get_json()
    logging.log(100, json_data) # write coordinates with user defined logging level
    return jsonify({'errMsg': '0'})
    

@api.route('/get_coordinates/')
def get_coordinates():
    return 'Hello get_coordinates!'
    # return jsonify(json_data)
