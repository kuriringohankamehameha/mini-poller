import os

PORT = os.environ.get('FLASK_PORT', 5000)

GUNICORN_WORKERS = os.environ.get('GUNICORN_WORKERS', 3)

bind = f"0.0.0.0:{PORT}"
loglevel = "INFO"
workers = f"{GUNICORN_WORKERS}"
reload = False

# errorlog = "logs/gunicorn/error.log"
# accesslog = "logs/gunicorn/access.log"