#!/bin/bash
set -e

pip install -r requirements.txt

gunicorn --config=gunicorn_config.py wsgi:app
