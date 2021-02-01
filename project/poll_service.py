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

import requests
from kafka import KafkaProducer
from kq import Job, Queue

from config import API_URLS, POLL_INTERVAL
from db_manager import MongoClient
from kafka_worker import KAFKA_URL
from utils import create_logger

DB_USER = os.environ.get('DB_USER', 'tester')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tester')
DB_NAME = os.environ.get('DB_NAME', 'test')
DB_PORT = os.environ.get('DB_PORT', '27017')
SERVER_URL = os.environ.get('SERVER_URL', '127.0.0.1')

logger = create_logger('poll-service')


def get_pending(tasks):
    results = [task for task in tasks if task != main_poller_task and task.done() == False]
    return results


def pass_to_message_queue(response):
    bytes_content = response.content
    logger.info(bytes_content.decode('utf-8'))


async def poll_endpoint(url):
    job = Job(func=requests.get, args=[url], timeout=POLL_INTERVAL)
    queue.enqueue(job)
    logger.info("Job Enqueued")
    # response = requests.get(url, timeout=POLL_INTERVAL)
    # pass_to_message_queue(response)


async def run_service(loop):
    curr = time.time()
    results = []

    while True:
        # First get the list of pending urls
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

    # Setup the Kafka Producer
    producer = KafkaProducer(bootstrap_servers=f"{KAFKA_URL}:9092")

    queue = Queue(topic='topic', producer=producer)

    try:
        loop.run_until_complete(main_poller_task)
    except Exception as ex:
        logger.critical(f"Encountered Exception: {ex}")
