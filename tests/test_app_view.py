import pytest
from page_analyzer.database_operations import PostgresqlOperations


@pytest.fixture()
def get_dict_from_select():
    datas = {'column_name': ('id', 'name'), 'rows': (('1', 'name1'), ('2', 'name2'))}
    result = ({'id': '1', 'name': 'name1'}, {'id': '2', 'name': 'name2'})
    return datas, result


@pytest.fixture()
def get_db():
    db = PostgresqlOperations('postgres://page_analyzer_base_84ng_user:Sat3BKyF60ZjNqRLg0lyton7w4Voeu03@dpg-cjb32ngc'
                              'fp5c73a6prk0-a.oregon-postgres.render.com/page_analyzer_base_84ng')
    return db


def test_insert(get_db):
    db = get_db
    db.insert('test_urls', name='name1')
    result = db.select(table_name='test_urls', fields_name='*')
    db.clear_table(table_name='test_urls')
    assert result[0]['name'] == 'name1'
