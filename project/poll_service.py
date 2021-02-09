import asyncio
import datetime
import itertools
import json
import logging
import os
import random
import threading
import time
from string import ascii_lowercase

import pika
import requests

from config import API_URLS, POLL_INTERVAL
from db_manager import MongoClient
from utils import create_logger

DB_USER = os.environ.get('DB_USER', 'tester')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tester')
DB_NAME = os.environ.get('DB_NAME', 'test')
DB_PORT = os.environ.get('DB_PORT', '27017')

BROKER_URL = os.getenv('RABBITMQ_BROKER_HOST', '127.0.0.1')

logger = create_logger('poll-service')

credentials, connection, channel = None, None, None

def perform_setup():
    """
    Sets up the relevant connections to the MQ and MongoDB
    """
    global credentials, connection, channel
    credentials = pika.PlainCredentials('guest', 'guest') # AUTH via Default guest user on RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbit-mq", 5672, '/', credentials)) # Using rabbit-mq container name to access the RabbitMQ container from other containers
    channel = connection.channel()
    channel.queue_declare(queue='poll', durable=True)


def perform_teardown():
    """
    Closes any relevant connections
    """
    global credentials, connection, channel
    connection.close()


def get_pending(tasks):
    """
    Retrieves a list of pending tasks from the event loop.
    Note that this is separate from the actual polled content,
    which is handled via the Message Queue.
    """
    results = [task for task in tasks if task != main_poller_task and task.done() == False]
    return results


async def poll_endpoint(url):
    """
    Performs a polling operation on a given endpoint asyncronously.
    This will publish messages to the Message Queue on a successful poll.
    Otherwise, we simply log the error during polling.
    """
    response = requests.get(url)
    if response.status_code not in [200, 201]:
        # Failures in the polling itself are being discarded here, due to a simple design
        # You could, however, have a second message queue filled with failed poll requests
        # and keep a dedicated consumer for that MQ.
        logger.critical(f"Error during polling {url}: Got response code - {response.status_code}")
    else:
        channel.basic_publish(exchange='', routing_key='poll', body=response.content, properties=pika.BasicProperties(delivery_mode=2))
        logger.info("Job Enqueued")


async def run_service(loop):
    """
    The async polling service
    """
    curr = time.time()
    results = []

    while True:
        # First get the list of pending tasks, if there exists any
        results = get_pending(results)

        # Now poll the endpoints
        for url in API_URLS:
            future = loop.create_task(poll_endpoint(url))
            results.append(future)
        
        await asyncio.gather(*results)
        
        delta = time.time() - curr
        diff = max(0, POLL_INTERVAL - delta)
        await asyncio.sleep(diff)
        curr = time.time()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main_poller_task = loop.create_task(run_service(loop))

    perform_setup()

    try:
        loop.run_until_complete(main_poller_task)
    except Exception as ex:
        logger.critical(f"Encountered Exception: {ex}")
    finally:
        perform_teardown()
