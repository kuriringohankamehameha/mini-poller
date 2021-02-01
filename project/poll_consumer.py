import datetime
import json
import os

import pika
import requests

from db_manager import MongoClient
from utils import create_logger

logger = create_logger('poll_consumer')

DB_USER = os.environ.get('DB_USER', 'tester')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tester')
DB_NAME = os.environ.get('DB_NAME', 'test')
DB_PORT = os.environ.get('DB_PORT', '27017')
SERVER_URL = os.environ.get('SERVER_URL', '127.0.0.1')

BROKER_URL = os.getenv('RABBITMQ_BROKER_HOST', '127.0.0.1')

credentials, connection, channel, db_client = None, None, None, None

def perform_setup():
    global credentials, connection, channel, db_client
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(BROKER_URL, 5672, '/', credentials))
    channel = connection.channel()
    channel.queue_declare(queue='poll', durable=True)

    # Database connection setup
    db_client = MongoClient(f"mongodb://{DB_USER}:{DB_PASSWORD}@{SERVER_URL}:{DB_PORT}/{DB_NAME}")
    db_client.connect(DB_NAME)


def perform_teardown():
    global credentials, connection, channel, db_client
    connection.close()


def process_request(body):
    """
    Processes the request body from the MQ and inserts into MongoDB
    """
    # Process the request and insert into MongoDB
    try:
        content = body.decode('utf-8')
        content = json.loads(content)
    except Exception as ex:
        logger.critical(f"Exception when decoding content: {ex}")
        return
    
    record = {**content, 'created_on': datetime.datetime.now()}
    record_id = db_client.insert_record(db_client.db_name, record)
    print(f"Inserted record: {record_id}")


def consume():
    """
    The Message Queue consumer, which continuously reads from the queue for any incoming messages
    """
    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        process_request(body) # byte encoded

    channel.basic_consume(queue='poll', auto_ack=True, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()


if __name__ == '__main__':
    perform_setup()
    try:
        consume()
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        perform_teardown()

