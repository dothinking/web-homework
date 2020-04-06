from flask import Blueprint, request, jsonify
import logging
import json
import pymongo
import time


api = Blueprint('api', __name__)
 
@api.route('/save_coordinate/', methods=['POST'])
def save_coordinate():
    json_data = request.get_json()
    logging.log(100, json.dumps(json_data)) # write coordinates with user defined logging level
    return jsonify({'errMsg': '0'})
    

@api.route('/get_coordinates/')
def get_coordinates():
    # connect to mongodb
    uri = 'mongodb://tom:goodboy@mongo:27017/app_coordinates'
    client = pymongo.MongoClient(uri)
    collection = client.app_coordinates.data

    # get latest 20 documents
    cursor_obj = collection.find().sort('timestamp', -1).limit(100)
    x, y = [], []
    for obj in cursor_obj:
        x.append({
            'value': [obj.get('timestamp'), obj.get('x')]
        })
        y.append({
            'value': [obj.get('timestamp'), obj.get('y')]
        })

    # prepare results
    res = {
        'x': x[::-1],
        'y': y[::-1]
    }
    return jsonify(res)
