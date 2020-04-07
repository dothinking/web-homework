from flask import Blueprint, request, jsonify
import logging
import json
import time
from .models import db


api = Blueprint('api', __name__)
 
@api.route('/save_coordinate/', methods=['POST'])
def save_coordinate():
    json_data = request.get_json()
    logging.log(100, json.dumps(json_data)) # write coordinates with user defined logging level
    return jsonify({'errMsg': '0'})
    

@api.route('/get_coordinates/')
def get_coordinates():
    # get documents within latest 1 min
    now = time.time()*1000
    past = now - 1 * 60 * 1000    
    x, y = [], []
    cursor_obj = db.data.find({ "timestamp" : { "$gte" : past, "$lt" : now } }).sort('timestamp')
    for obj in cursor_obj:
        x.append({
            'value': [obj.get('timestamp'), obj.get('x')]
        })
        y.append({
            'value': [obj.get('timestamp'), obj.get('y')]
        })

    # prepare results
    return jsonify({
        'x': x,
        'y': y,
        'z': [{'value': [past, 0]}, {'value': [now, 0]}] # dummy series
    })
