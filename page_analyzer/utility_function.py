import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse
from page_analyzer.database_operations import PostgresqlOperations


load_dotenv()


def get_db():
    database_url = os.getenv('DATABASE_URL')
    db = PostgresqlOperations(database_url)
    return db


def get_site_info(sites_url):
    page = requests.get(sites_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    status_code = page.status_code

    match status_code == 200:
        case True:
            h1 = soup.find('h1').get_text() if soup.find('h1') else ''
            title = soup.find('title').get_text() if soup.find('title') else ''
            description = soup.find(attrs=({'name': 'description'})).get('content') \
                if soup.find(attrs=({'name': 'description'})) else ''
            result = {'h1': h1, 'title': title, 'description': description, 'status_code': status_code}
            return result
        case False:
            return False


def get_url(url):
    return f"{urlparse(url).scheme}://{urlparse(url).netloc}"
