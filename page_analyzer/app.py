import requests
import os
from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from urllib.parse import urlparse
from validators import url
from page_analyzer.database_operations import PostgresqlOperations
from bs4 import BeautifulSoup


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')

db = PostgresqlOperations(DATABASE_URL)


def get_site_info(sites_url):
    page = requests.get(sites_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    status_code = page.status_code
    if status_code == 200:
        h1 = soup.find('h1').get_text() if soup.find('h1') else ''
        title = soup.find('title').get_text() if soup.find('title') else ''
        description = soup.find(attrs=({'name': 'description'})).get('content') \
            if soup.find(attrs=({'name': 'description'})) else ''
        result = {'h1': h1, 'title': title, 'description': description, 'status_code': status_code}
        return result
    else:
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def request_processing():
    # возможно обработчик поменять на /urls
    entered_request = request.form.to_dict()['url']
    url_site = f"{urlparse(entered_request).scheme}://{urlparse(entered_request).netloc}"

    if not entered_request:
        flash('URL обязателен')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)
    elif url(url_site) is not True:
        flash('Некорректный URL')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)
    elif url(url_site) is True:
        if db.check_exists(table_name='urls', fields_name='name', condition=f"name = '{url_site}'")['answer'] is False:
            flash('Страница успешно добавлена', 'success')

        db.insert_unique("urls", name=url_site)
        url_id = db.select('urls', fields_name=('id',), condition=f"name = '{url_site}'")[0]['id']

        return redirect(url_for('show_site_info', site_id=url_id))


@app.route('/urls', methods=['GET'])
def get_sites_list():
    sites_list = db.select_special()

    return render_template('sites.html', sites_list=sites_list)


@app.route('/urls/<site_id>', methods=['GET'])
def show_site_info(site_id):

    messages = get_flashed_messages(with_categories=True)
    url_info = db.select('urls', fields_name=('id', 'name', 'DATE(created_at)'), condition=f"id = {site_id}")
    checks_list = db.select(table_name='url_checks',
                            fields_name=('id', 'status_code', 'h1', 'title', 'description', 'DATE(created_at)'),
                            condition=f"url_id = {site_id}",
                            fields_order='id', order='DESC')

    return render_template('url_info.html', url_info=url_info, checks_list=checks_list, messages=messages)


@app.route('/urls/<site_id>/checks', methods=['POST'])
def check_url(site_id):
    url_site = db.select('urls', fields_name=('name',), condition=f"id = {site_id}")[0]['name']
    checks_result = get_site_info(url_site)
    if checks_result is False:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_site_info', site_id=site_id))
    else:
        flash('Страница успешно проверена', 'success')
        db.insert("url_checks",
                  url_id=site_id,
                  status_code=checks_result['status_code'],
                  h1=checks_result['h1'],
                  title=checks_result['title'],
                  description=checks_result['description'])

    return redirect(url_for('show_site_info', site_id=site_id))
