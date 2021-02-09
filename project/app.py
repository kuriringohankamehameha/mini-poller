import datetime
import io
import itertools
import json
import logging
import os
import random
import socket
import threading
import time
from string import ascii_lowercase

import pymongo
import requests
from flask import Flask, Response, render_template, request

from config import API_URLS, POLL_INTERVAL
from db_manager import MongoClient
from utils import create_logger

DB_USER = os.environ.get('DB_USER', 'tester')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tester')
DB_NAME = os.environ.get('DB_NAME', 'test')
DB_PORT = os.environ.get('DB_PORT', '27017')
SERVER_URL = os.environ.get('SERVER_URL', '127.0.0.1')

# logger = create_logger('app')

app = Flask(__name__)

@app.route(f'/list', methods=['GET'])
def _list():
    client = MongoClient(f"mongodb://{DB_USER}:{DB_PASSWORD}@{SERVER_URL}:{DB_PORT}/{DB_NAME}")
    client.connect(DB_NAME)
    cursor = client.find_all(DB_NAME, {})
    response = client.fetch_all(cursor, container=[], func='append')
    return json.dumps(str(response))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/listall', methods=['GET'])
def listall():
    res = []
    hostname = '127.0.0.1'
    port = 27017
    username = 'tester'
    password = 'tester'
    databaseName = 'test'

    # connect with authentication
    client = MongoClient(hostname, port)
    db = client[databaseName]
    db.authenticate(username, password)

    collection = db['test']
    cursor = collection.find({})
    for document in cursor:
        res.append(document)
    
    return json.dumps(res)


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
