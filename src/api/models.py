import pymongo

# connect to mongodb
client = pymongo.MongoClient(
    host='mongo',
    port=27017,
    username='tom',
    password='goodboy',
    authSource='app_coordinates')

# database name: app_coordinates
db = client['app_coordinates']