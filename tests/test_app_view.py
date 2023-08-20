import pytest
from page_analyzer.database_operations import PostgresqlOperations
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

@pytest.fixture()
def get_dict_from_select():
    datas = {'column_name': ('id', 'name'), 'rows': (('1', 'name1'), ('2', 'name2'))}
    result = ({'id': '1', 'name': 'name1'}, {'id': '2', 'name': 'name2'})
    return datas, result


@pytest.fixture()
def get_db():
    db = PostgresqlOperations(DATABASE_URL)
    return db


def test_insert(get_db):
    db = get_db
    result = db.select(table_name='urls', fields_name='*')
    assert len(result) > 0
