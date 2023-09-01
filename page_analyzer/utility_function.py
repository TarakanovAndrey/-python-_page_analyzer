import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


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


def collect_url(url):
    return f"{urlparse(url).scheme}://{urlparse(url).netloc}"


def union_datas(data1, data2):
    result = list()

    for value1 in data1:
        result.append(dict())
        for value2 in data2:
            if value1['id'] == value2['url_id']:
                result[-1]['id'] = value1['id']
                result[-1]['name'] = value1['name']
                result[-1]['status_code'] = value2['status_code']
                result[-1]['data'] = value2['max']
        if not result[-1]:
            result[-1]['id'] = value1['id']
            result[-1]['name'] = value1['name']
            result[-1]['status_code'] = ' '
            result[-1]['data'] = ' '
    return result
