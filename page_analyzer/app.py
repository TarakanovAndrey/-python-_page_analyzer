import os
from validators import url
from page_analyzer.utility_function import get_db
from page_analyzer.utility_function import get_url
from page_analyzer.utility_function import get_site_info
from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = get_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def request_processing():
    entered_url = request.form['url']
    if not entered_url:
        flash('URL обязателен')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)

    url_site = get_url(entered_url)

    if not url(url_site, public=True):
        flash('Некорректный URL')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages), 422
    elif url(url_site, public=True):
        check_urls_exist = db.check_urls_exist(url_site)
        if not check_urls_exist:
            db.urls_insert_url(url_site)
            url_id = db.urls_get_id(url_site)
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('show_site_info', site_id=url_id))

        elif check_urls_exist:
            flash('Страница уже существует', 'success')
            url_id = db.urls_get_id(url_site)
            return redirect(url_for('show_site_info', site_id=url_id))


@app.route('/urls', methods=['GET'])
def get_sites_list():
    sites_list = db.selecting_summary_information()
    return render_template('sites.html', sites_list=sites_list)


@app.route('/urls/<site_id>', methods=['GET'])
def show_site_info(site_id):
    messages = get_flashed_messages(with_categories=True)
    url_info = db.urls_get_urls_info(site_id)
    checks_list = db.url_checks_get_checks_info(site_id)

    return render_template('url_info.html', url_info=url_info, checks_list=checks_list, messages=messages)


@app.route('/urls/<site_id>/checks', methods=['POST'])
def check_url(site_id):
    url_site = db.urls_get_url(site_id)
    checks_result = get_site_info(url_site)
    if checks_result is False:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        db.url_checks_insert_result(site_id, checks_result)

    return redirect(url_for('show_site_info', site_id=site_id))
