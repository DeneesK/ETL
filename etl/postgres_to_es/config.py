import os
import json
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from psycopg2.errors import Error
from elasticsearch import exceptions


# Loading environment variables
load_dotenv()

LOGGER_SETTINGS = {
    "format": "%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "handlers": [RotatingFileHandler('logs.log', maxBytes=2000000, backupCount=2)],
    "level": logging.INFO
}

index = os.environ.get('INDEX_NAME')  # Название индекса ES
logging.basicConfig(**LOGGER_SETTINGS)
logger = logging.getLogger(__name__)

dsl = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('USER_NAME'),
    'password': os.environ.get('PASSWORD'),
    'host': os.environ.get('HOST'),
    'port': os.environ.get('DB_PORT'),
}

ES_HOST = os.environ.get('ES_HOST')

BACKOFF_CONFIG = {
    "exception": (Error, exceptions.ConnectionError),
    "logger": logger,
    "max_time": 600
}

# Settings for creating index on ES
with open('settings.json', 'r') as file:
    SETTINGS = json.load(file)
