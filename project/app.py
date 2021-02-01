import datetime
import io
import itertools
import json
import logging
import os
import random
import threading
import time
from string import ascii_lowercase

import requests
from flask import Flask, Response, request

from config import API_URLS, POLL_INTERVAL
from db_manager import MongoClient
from utils import create_logger

DB_USER = os.environ.get('DB_USER', 'tester')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tester')
DB_NAME = os.environ.get('DB_NAME', 'test')
DB_PORT = os.environ.get('DB_PORT', '27017')
SERVER_URL = os.environ.get('SERVER_URL', '127.0.0.1')


def background_thread():
    print("Background Thread started!")
    i=0
    while True:
        if i % 240 == 0:
            i = 0
            ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
            tmp = ist_time.strftime("%H:%m")
            hours, minutes = int(tmp.split(":")[0]), int(tmp.split(":")[1])
            if hours >= 2 and hours <= 9:
                pass
            else:
                _ = requests.get('https://google.com')
        i += 1
        time.sleep(5)


logger = create_logger('app')

app = Flask(__name__)


@app.route(f'/receive', methods=['GET'])
def receive():
    return Response(f"Timeout Exceeded", status=400)


@app.route(f'/list', methods=['GET'])
def _list():
    client = MongoClient(f"mongodb://{DB_USER}:{DB_PASSWORD}@{SERVER_URL}:{DB_PORT}/{DB_NAME}")
    client.connect(DB_NAME)
    
    record = {'title': "".join([random.choice(ascii_lowercase) for _ in range(10)]), 'text': 'Sample Text', 'value': 100, 'created_on': datetime.datetime.now()}

    record_id = client.insert_record(client.db, record)
    print(f"Inserted record: {record_id}")

    cursor = client.find_all(client.db, {})

    response = client.fetch_all(cursor, container=[], func='append')

    return json.dumps(str(response))



@app.route(f'/', methods=['POST'])
def respond():
    json_data = request.get_json(force=True)    
    return json_data


@app.route('/setwebhook', methods=['POST'])
def set_webhook():
    return Response("Webhook setup OK", status=200)


@app.route('/')
def index():
    return 'This is the Home Page.'

if __name__ == '__main__':
    app.run(threaded=True, debug=True)
