from flask import Flask, render_template, request, url_for, redirect
import psycopg2
from urllib.parse import urlparse
from validators import url
import os
from datetime import datetime, date, time
from page_analyzer.database_operations import PostgresqlOperations
from itertools import chain
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SJLDFJSLJDLJAJSLKDJFLSJF'

db = PostgresqlOperations(user='andrey', password='password', database='database')


def get_site_info(sites_url):

    page = requests.get(sites_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    h1 = soup.find('h1').get_text() if soup.find('h1') else ''
    title = soup.find('title').get_text() if soup.find('title') else ''
    description = soup.find(attrs=({'name': 'description'})).get('content') if soup.find(attrs=({'name': 'description'})) else ''
    status_code = page.status_code if page.status_code else ''
    result = {'h1': h1, 'title': title, 'description': description, 'status_code': status_code}
    return result



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def request_processing():
    entered_request = request.form.to_dict()['url']
    url_site = urlparse(entered_request).scheme + '://' + urlparse(entered_request).netloc
    dates_create = datetime.now().date()

    if url(url_site) is True:
        db.insert_unique("sites_list", name=url_site, created_at=dates_create)

    rows_id = db.select('sites_list', fields_name='*', condition=f"name = '{url_site}'")['id']
    # еще раз посмотреть про вставку с возвратом последней вставленной строки
    return redirect(url_for('show_site_info', site_id=rows_id, url_site=url_site))


@app.route('/urls', methods=['GET'])
def get_sites_list():
    sites_list = db.select(table_name='sites_list', fields_name='*', fields_order='id', order='DESC')
    return render_template('sites.html', sites_list=sites_list)


@app.route('/urls/<site_id>', methods=['GET'])
def show_site_info(site_id):
    url_info = db.select('sites_list', fields_name='*', condition=f"id = {site_id}")

    checks_list = db.select(table_name='checks_info', fields_name='*', condition=f"sites_list_id = {site_id}", fields_order='id', order='DESC')

    return render_template('url_info.html', url_info=url_info, checks_list=checks_list)



@app.route('/urls/<site_id>/checks', methods=['POST'])
def check_url(site_id):
    url_site = db.select('sites_list',  fields_name='*', condition=f"id = {site_id}")['name']

    checks_result = get_site_info(url_site)

    dates_create = datetime.now().date()
    db.insert("checks_info",
              sites_list_id=site_id,
              code_response=checks_result['status_code'],
              h1=checks_result['h1'],
              title=checks_result['title'],
              description=checks_result['description'],
              created_at=dates_create)

    db.update(table='sites_list', field_name=f"date_last_check = '{dates_create}', last_code_response = '{checks_result['status_code']}'", condition=f"name = '{url_site}'")

    return redirect(url_for('show_site_info', site_id=site_id))
