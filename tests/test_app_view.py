import pytest
from page_analyzer.utility_function import datas_to_dict
from page_analyzer.app import app
from page_analyzer.database_operations import PostgresqlOperations


@pytest.fixture()
def get_dict_from_select():
    datas = {'column_name': ('id', 'name'), 'rows': (('1', 'name1'), ('2', 'name2'))}
    result = ({'id': '1', 'name': 'name1'}, {'id': '2', 'name': 'name2'})
    return datas, result


@pytest.fixture()
def get_app():
    app.config.update({'TESTING': True})
    yield app


@pytest.fixture()
def get_db():
    db = PostgresqlOperations('postgres://page_analyzer_base_84ng_user:Sat3BKyF60ZjNqRLg0lyton7w4Voeu03@dpg-cjb32ngc'
                              'fp5c73a6prk0-a.oregon-postgres.render.com/page_analyzer_base_84ng')
    return db


@pytest.fixture()
def client(get_app):
    return app.test_client()


@pytest.fixture()
def runner(get_app):
    return app.test_cli_runner()


def test_get_dict_from_select(get_dict_from_select):
    datas, result = get_dict_from_select
    assert datas_to_dict(datas) == result


def test_insert(get_db):
    db = get_db
    db.insert('test_urls', name='name1')
    result = db.select(table_name='test_urls', fields_name='*')
    assert result[0]['name'] == 'name1'


def test_correct_url(client, get_db):
    response = client.post('/urls', data={'url': 'https://flask.palletsprojects.com'})
    assert response.status_code == 302


def test_empty_request(client):
    response = client.post('/urls', data={'url': ''})
    assert response.status_code == 200
    assert response.request.path == '/urls'


def test_wrong_url(client):
    response = client.post('/urls', data={'url': 'sdfsdfs'})
    assert response.status_code == 422
    assert response.request.path == '/urls'
