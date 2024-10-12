from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            load_dotenv()
            ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
            ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
            ELASTIC_URL = os.getenv('ELASTIC_URL')

            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.db = Elasticsearch(
                [ELASTIC_URL],
                basic_auth = (ELASTIC_USERNAME, ELASTIC_PASSWORD),
                headers = {"Content-Type": "application/json"},
                api_version = '7.10.1'
            )
        return cls._instance
