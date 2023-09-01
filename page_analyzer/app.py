import os
from validators import url
from page_analyzer.utility_function import collect_url, get_site_info, union_datas
from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from page_analyzer.database_operations import (insert_checks_result,
                                               insert_url, get_id,
                                               get_url_info,
                                               get_sites_url,
                                               get_checks_info_of_url,
                                               check_urls_exist,
                                               get_urls_info,
                                               get_checks_info)

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

    if not check_exist:
        url_id = insert_url(url_site)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', site_id=url_id))

    elif check_exist:
        url_id = get_id(url_site)
        flash('Страница уже существует', 'success')
        return redirect(url_for('get_url', site_id=url_id))


@app.route('/urls', methods=['GET'])
def list_urls():
    urls_info = get_urls_info()
    checks_info = get_checks_info()
    union_info = union_datas(urls_info, checks_info)

    return render_template('sites.html', sites_list=union_info)


@app.route('/urls/<site_id>', methods=['GET'])
def get_url(site_id):
    messages = get_flashed_messages(with_categories=True)
    url_info = get_url_info(site_id)
    checks_list = get_checks_info_of_url(site_id)

    return render_template('url_info.html',
                           url_info=url_info,
                           checks_list=checks_list,
                           messages=messages)


@app.route('/urls/<site_id>/checks', methods=['POST'])
def check_url(site_id):
    url_site = get_sites_url(site_id)
    checks_result = get_site_info(url_site)
    if checks_result is False:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        insert_checks_result(site_id, checks_result)

    return redirect(url_for('get_url', site_id=site_id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
