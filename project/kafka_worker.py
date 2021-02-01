import logging
import os

from kafka import KafkaConsumer
from kq import Worker

# from utils import create_logger

# logger = create_logger('kq-worker')

# Set up logging.
formatter = logging.Formatter('[%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger('kq.worker')
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

KAFKA_URL = os.environ.get('KAFKA_ADVERTISED_HOST_NAME', '127.0.0.1')


def callback(status, message, job, result, exception, stacktrace):
    if status == 'success':
        # Job completed
        logger.info("Job Success")
    elif status in ['failure', 'invalid']:
        # Failure
        logger.critical("Job Failed")
    elif status == 'timeout':
        # Timeout
        logger.warning("Job Timeout")
    else:
        logger.critical(f"Unknown status: {status}")


if __name__ == '__main__':
    # Set up a Kafka consumer.
    consumer = KafkaConsumer(
        bootstrap_servers=f'{KAFKA_URL}:9092',
        group_id='group',
        auto_offset_reset='latest'
    )

    # Set up a worker.
    worker = Worker(topic='topic', consumer=consumer, callback=callback)
    worker.start()
