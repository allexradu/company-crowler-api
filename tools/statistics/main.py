from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from models.website_data import WebsiteData


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


def main():
    # Get the count of all records in the 'website_data' index
    count_response = es.count(index = 'website_data')
    total_records = count_response['count']

    print(f'Total number of websites in queue: {total_records}')

    # Query to get the count of records where the 'error' field is null
    query = {
        "query": {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "error"
                    }
                }
            }
        }
    }

    # Execute the count query
    count_response = es.count(index = 'website_data', body = query)
    total_records_successfully_scraped = count_response['count']

    if total_records > 0:
        percentage_successfully_scraped = (total_records_successfully_scraped / total_records) * 100
        print(
            f'Total number of website successfully scraped: {total_records_successfully_scraped} ( {percentage_successfully_scraped:.2f}% )')
    else:
        print('No records found in the index.')

    # Initialize the scroll
    response = es.search(index = 'website_data', body = query, scroll = '2m', size = 1000)
    scroll_id = response['_scroll_id']
    all_records = response['hits']['hits']

    # Scroll through the results
    while len(response['hits']['hits']):
        response = es.scroll(scroll_id = scroll_id, scroll = '2m')
        scroll_id = response['_scroll_id']
        all_records.extend(response['hits']['hits'])

    data_points = 0

    for record in all_records:
        data = WebsiteData(**record['_source'])
        data_points += len(data.phone_numbers)
        data_points += len(data.social_links['facebook'])
        data_points += len(data.social_links['twitter'])
        data_points += len(data.social_links['linkedin'])
        data_points += len(data.social_links['instagram'])

    print(f'Total data points extracted: {data_points}')


if __name__ == "__main__":
    main()
