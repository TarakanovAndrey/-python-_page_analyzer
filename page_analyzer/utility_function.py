import requests
from bs4 import BeautifulSoup


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


def datas_to_dict(items):
    keys = items['column_name']
    values = items['rows']
    rows = list()
    for item in values:
        dict_ = {}
        for key, value in zip(keys, item):
            if value is None:
                value = ''
                dict_[key] = value
            dict_[key] = value
        rows.append(dict_)

    return tuple(rows)
