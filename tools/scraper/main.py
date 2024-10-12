import asyncio
import os
import random
import re
import time
from urllib.parse import urljoin

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from models.website_data import WebsiteData

# Load environment variables
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

# Load the list of websites
websites_df = pd.read_csv(os.path.join(os.path.curdir, 'assets/csvs/sample-websites.csv'))
websites = ['http://' + domain if not domain.startswith('http') else domain for domain in
            websites_df['domain'].tolist()]

# websites = websites[:100]  # Limit the number of websites to crawl

# Regex patterns for data extraction
PHONE_PATTERN = r'\(\d{3}\) \d{3}-\d{4}'
SOCIAL_PATTERNS = {
    'facebook': r'facebook\.com/[a-zA-Z0-9_.-]+',
    'twitter': r'twitter\.com/[a-zA-Z0-9_.-]+',
    'linkedin': r'linkedin\.com/[a-zA-Z0-9_.-]+',
    'instagram': r'instagram\.com/[a-zA-Z0-9_.-]+'
}

# Headers to mimic a regular browser
HEADERS_LIST = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
    },
    {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
    }
]


# Extract data from a single website using multiple methods
async def extract_data(url, session):
    try:
        # Method 1: Using aiohttp
        headers = random.choice(HEADERS_LIST)
        async with session.get(url, headers = headers, timeout = 10) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                return await parse_data(url, soup, html_content, session)
    except Exception as e:
        print(f"aiohttp failed for {url}: {e}")

    try:
        # Method 2: Using BeautifulSoup with requests
        headers = random.choice(HEADERS_LIST)
        response = requests.get(url, headers = headers, timeout = 10)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            return await parse_data(url, soup, html_content, session)
    except Exception as e:
        print(f"BeautifulSoup with requests failed for {url}: {e}")

    return None


# Parse data using BeautifulSoup
async def parse_data(url, soup, html_content, session):
    # Extract phone numbers
    phone_numbers = re.findall(PHONE_PATTERN, html_content)

    # Extract social media links
    social_links = {key: [] for key in SOCIAL_PATTERNS.keys()}
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = re.findall(pattern, html_content)
        matches = [url.lower() for url in matches]
        if matches:
            social_links[platform].extend(matches)

    # Extract all links on the page
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href = True)]

    contact_page = None
    # Find and scrape 'contact' page if available
    for link in links:
        if 'contact' in link.lower():
            contact_page = link

    phone_numbers = list(set(phone_numbers))
    phone_numbers = [re.sub(r'[^\d+]', '', number) for number in phone_numbers]

    for key in social_links:
        social_links[key] = list(set(social_links[key]))

    return WebsiteData(url = url, phone_numbers = phone_numbers, social_links = social_links,
                       contact_page = contact_page)


def write_data_to_elastic_search(data: WebsiteData, url):
    try:
        response = es.index(index = 'website_data', body = data.__dict__)
        print(response)
    except Exception as e:
        print(f"Failed to index data for {url}: {e}")


async def crawl_website(url, session):
    try:
        data = await extract_data(url, session)
        print('data: ', data)
        if data:
            if data.contact_page:
                contact_data = await extract_data(data.contact_page, session)
                print('contact_data: ', contact_data)
                if contact_data:
                    data.phone_numbers.extend(contact_data.phone_numbers)
                    for key in data.social_links:
                        data.social_links[key].extend(contact_data.social_links[key])

            # Remove duplicates using a set
            data.phone_numbers = list(set(data.phone_numbers))
            data.phone_numbers = [re.sub(r'[^\d+]', '', number) for number in data.phone_numbers]

            for key in data.social_links:
                data.social_links[key] = list(set(data.social_links[key]))

            write_data_to_elastic_search(data, url)

        else:
            error_message = f"Failed to crawl {url}: No data extracted."
            data = WebsiteData(url = url, error = error_message)
            write_data_to_elastic_search(data, url)
            print(error_message)

    except Exception as e:
        # If an error occurs, store the URL in Elasticsearch with an error message
        error_message = f"Failed to crawl {url}: {e}"
        data = WebsiteData(url = url, error = error_message)
        write_data_to_elastic_search(data, url)
        print(error_message)


# Crawl all websites concurrently and store data in Elasticsearch
async def crawl_websites(sites):
    async with aiohttp.ClientSession() as session:
        tasks = [crawl_website(website, session) for website in sites]
        return await asyncio.gather(*tasks)


# Run the crawler and analyze results
def main():
    start_time = time.time()
    asyncio.run(crawl_websites(websites))
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes = int(elapsed_time // 60)
    elapsed_seconds = elapsed_time % 60
    print(
        f"Data extraction and indexing to Elasticsearch completed"
        f" in {elapsed_minutes} minutes and {elapsed_seconds:.2f} seconds."
    )


if __name__ == "__main__":
    main()
