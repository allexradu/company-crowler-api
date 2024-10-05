from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_URL = os.getenv('ELASTIC_URL')

es = Elasticsearch(
    [ELASTIC_URL],
    basic_auth = (ELASTIC_USERNAME, ELASTIC_PASSWORD),
    headers = {"Content-Type": "application/json"},
    api_version = '7.10.1'
)

result = {
    'url': 'https://google2.com',
}

# Delete all documents from the index
try:
    response = es.delete_by_query(index = 'website_data', body = {"query": {"match_all": {}}})
    print(response)
except Exception as e:
    print(f"Failed to delete documents: {e}")
