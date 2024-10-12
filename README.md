# Company Data Scraper:

### BEFORE EVERYTHING:

##### 1) Set .env file with the variables like in .env.example

##### 2) Run the following command to install the requirements:

```pip install -r requirements.txt```

##### 3) Run the docker-compose command:

```docker-compose up --build```

### #1 Run the Scraping tool with the command:

```python tools/scraper/main.py```

### #2 Run the Scalable Scraping tool:

#### 1) Run First celery

```celery -A tools.scalable_scraper.worker worker --loglevel=info --concurrency=30 --purge```

#### 2) Run the scalable scraper

```python tools/scalable_scraper/main.py```

### #3 Run the statistics tool to get stats about the scraped data:

```python tools/stats/main.py```

### #4 Run merge tool to merge company data:

```python tools/merge_company_data/main.py```

### #5 Run the API:

```python api/main.py```

###### Navigate to http://localhost:8000 to see the API documentation

### #6 Run the Data Cleaning tool with the command:

```python tools/clean_elastic_search/main.py```