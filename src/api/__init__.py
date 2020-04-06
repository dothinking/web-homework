import logging

logging.basicConfig(
    level=100, # user defined level, just for writing user data
    filename='../data/coordinates.log', # relative to app.py calling this __init__.py
    filemode='a',
    format='%(message)s'
)