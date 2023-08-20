import os
from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from urllib.parse import urlparse
from validators import url
from page_analyzer.database_operations import PostgresqlOperations
from dotenv import load_dotenv
from page_analyzer.utility_function import get_site_info

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')
db = PostgresqlOperations(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def request_processing():
    entered_request = request.form.to_dict()['url']
    url_site = f"{urlparse(entered_request).scheme}://{urlparse(entered_request).netloc}"

    if not entered_request:
        flash('URL обязателен')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)
    elif not url(url_site, public=True):
        flash('Некорректный URL')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages), 422
    elif url(url_site, public=True):
        check_exists = db.check_exists(table_name='urls',
                                       fields_name='name',
                                       condition=f"name = '{url_site}'")['answer']

        if not check_exists:
            db.insert_unique(table_name="urls", name=url_site)
            url_id = db.select(table_name='urls', fields_name=('id',), condition=f"name = '{url_site}'")[0]['id']
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('show_site_info', site_id=url_id))

        elif check_exists:
            flash('Страница уже существует', 'success')
            url_id = db.select(table_name='urls', fields_name=('id',), condition=f"name = '{url_site}'")[0]['id']
            return redirect(url_for('show_site_info', site_id=url_id))


@app.route('/urls', methods=['GET'])
def get_sites_list():
    sites_list = db.select_special()

    return render_template('sites.html', sites_list=sites_list)


@app.route('/urls/<site_id>', methods=['GET'])
def show_site_info(site_id):
    messages = get_flashed_messages(with_categories=True)
    url_info = db.select(table_name='urls', fields_name=('id', 'name', 'DATE(created_at)'), condition=f"id = {site_id}")
    checks_list = db.select(table_name='url_checks',
                            fields_name=('id', 'status_code', 'h1', 'title', 'description', 'DATE(created_at)'),
                            condition=f"url_id = {site_id}",
                            fields_order='id', order='DESC')

    return render_template('url_info.html', url_info=url_info, checks_list=checks_list, messages=messages)


@app.route('/urls/<site_id>/checks', methods=['POST'])
def check_url(site_id):
    url_site = db.select(table_name='urls', fields_name=('name',), condition=f"id = {site_id}")[0]['name']
    checks_result = get_site_info(url_site)
    if checks_result is False:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        db.insert(table_name="url_checks",
                  url_id=site_id,
                  status_code=checks_result['status_code'],
                  h1=checks_result['h1'],
                  title=checks_result['title'],
                  description=checks_result['description'])

    return redirect(url_for('show_site_info', site_id=site_id))
