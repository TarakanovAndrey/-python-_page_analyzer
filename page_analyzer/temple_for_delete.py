from bs4 import BeautifulSoup
import requests

import datetime
from collections import defaultdict
# def f(*args, **kwargs):
#     fields_name = ', '.join(kwargs.keys())
#     print(fields_name)
#     values = ', '.join(f"'{x}'" for x in kwargs.values())
#     print(values)
#
#
# print(f('sites', name='render.com', date='34344'))
#
#
# # """
# CREATE TABLE sites (
# id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
# name varchar(255) UNIQUE,
# created_at date
# );
# #
# #
# # """


# def get_site_info(sites_url):
#
#     page = requests.get(sites_url)
#     soup = BeautifulSoup(page.text, 'html.parser')
#
#     h1 = soup.find('h1').get_text() if soup.find('h1') else ''
#     title = soup.find('title').get_text() if soup.find('title') else ''
#
#     description = soup.find(attrs=({'name': 'description'})).get('content') if soup.find(attrs=({'name': 'description'})) else ''
#     status_code = page.status_code if page.status_code else ''
#     result = {'h1': h1, 'title': title, 'description': description, 'status_code': status_code}
#     return result
#
#
# print(get_site_info('https://ru.hexlet.io'))



