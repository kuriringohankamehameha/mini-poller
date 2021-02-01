#!/bin/bash
set -e

pip install -r requirements.txt

# gunicorn wsgi:app --workers $GUNICORN_WORKERS --bind 0.0.0.0:$FLASK_PORT
# gunicorn --config=gunicorn_config.py wsgi:app

# python3 poll_service.py