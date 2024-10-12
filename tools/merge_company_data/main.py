import os
import pandas as pd
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_URL = os.getenv('ELASTIC_URL')

# Initialize Elasticsearch client
es = Elasticsearch(
    [ELASTIC_URL],
    basic_auth = (ELASTIC_USERNAME, ELASTIC_PASSWORD),
    headers = {"Content-Type": "application/json"},
    api_version = '7.10.1'
)


def get_record_id(url):
    query = {
        "query": {
            "match": {
                "url": url
            }
        }
    }

    # Execute the search query
    response = es.search(index = 'website_data', body = query)

    # Extract the records from the response
    records = response['hits']['hits']

    if records:
        return records[0]['_id']
    else:
        return None


def main():
    company_data_df = pd.read_csv(os.path.join(os.path.curdir, 'assets/csvs/sample-websites-company-names.csv'))

    company_data_df['domain'] = company_data_df['domain'].apply(
        lambda x: 'http://' + x if not x.startswith('http') else x)

    for index, row in company_data_df.iterrows():
        url = row['domain']
        all_company_names = []
        commercial_names = None
        legal_name = None

        if pd.notna(row['company_commercial_name']):
            commercial_names = row['company_commercial_name'].split(' | ')
            all_company_names.extend(commercial_names)

        if pd.notna(row['company_legal_name']):
            legal_name = row['company_legal_name']
            all_company_names.append(legal_name)

        if pd.notna(row['company_all_available_names']):
            company_all_available_names = row['company_all_available_names'].split(' | ')
            [all_company_names.append(company_name) for company_name in company_all_available_names if
             company_name not in all_company_names]

        record_id = get_record_id(url)

        new_fields = {
            "legal_name": legal_name,
            "commercial_names": commercial_names,
            "all_company_names": all_company_names,
        }

        response = es.update(
            index = 'website_data',
            id = record_id,
            body = {
                "script": {
                    "source": "ctx._source.putAll(params.new_fields)",
                    "params": {
                        "new_fields": new_fields
                    }
                }
            }
        )

        print(
            f'{url} - {commercial_names} - {legal_name}  -  {all_company_names} -  {record_id}'
        )
        print(response)


if __name__ == '__main__':
    main()
