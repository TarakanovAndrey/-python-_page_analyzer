import os
from validators import url
from page_analyzer.utility_function import collect_url
from page_analyzer.utility_function import get_site_info
from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from page_analyzer.database_operations import (url_checks_insert_result,
                                               urls_insert_url, urls_get_id,
                                               urls_get_urls_info,
                                               urls_get_url,
                                               url_checks_get_checks_info,
                                               selecting_summary_information,
                                               check_urls_exist)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def post_url():
    entered_url = request.form['url']
    if not entered_url:
        flash('URL обязателен')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)

    url_site = collect_url(entered_url)
    validate_url = url(url_site, public=True)

    if not validate_url:
        flash('Некорректный URL')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages), 422

    check_exist = check_urls_exist(url_site)

    if validate_url and not check_exist:
        url_id = urls_insert_url(url_site)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', site_id=url_id))

    elif validate_url and check_exist:
        url_id = urls_get_id(url_site)
        flash('Страница уже существует', 'success')
        return redirect(url_for('get_url', site_id=url_id))


@app.route('/urls', methods=['GET'])
def list_urls():
    sites_list = selecting_summary_information()
    return render_template('sites.html', sites_list=sites_list)


@app.route('/urls/<site_id>', methods=['GET'])
def get_url(site_id):
    messages = get_flashed_messages(with_categories=True)
    url_info = urls_get_urls_info(site_id)
    checks_list = url_checks_get_checks_info(site_id)

    return render_template('url_info.html', url_info=url_info, checks_list=checks_list, messages=messages)


@app.route('/urls/<site_id>/checks', methods=['POST'])
def check_url(site_id):
    url_site = urls_get_url(site_id)
    checks_result = get_site_info(url_site)
    if checks_result is False:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        url_checks_insert_result(site_id, checks_result)

    return redirect(url_for('get_url', site_id=site_id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
