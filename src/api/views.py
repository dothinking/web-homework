from flask import Blueprint, request, jsonify
import logging
import json
from .models import db


api = Blueprint('api', __name__)
 
@api.route('/save_coordinate/', methods=['POST'])
def save_coordinate():
    json_data = request.get_json()
    logging.log(100, json.dumps(json_data)) # write coordinates with user defined logging level
    return jsonify({'errMsg': '0'})
    

@api.route('/get_coordinates/')
def get_coordinates():
    # get latest 20 documents
    x, y = [], []
    cursor_obj = db.data.find().sort('timestamp', -1).limit(100)
    for obj in cursor_obj:
        x.append({
            'value': [obj.get('timestamp'), obj.get('x')]
        })
        y.append({
            'value': [obj.get('timestamp'), obj.get('y')]
        })

    # prepare results
    return jsonify({
        'x': x[::-1],
        'y': y[::-1]
    })
