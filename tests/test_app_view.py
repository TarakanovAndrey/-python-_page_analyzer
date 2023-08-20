import pytest
import os
from page_analyzer.database_operations import PostgresqlOperations
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


@pytest.fixture()
def get_db():
    db = PostgresqlOperations(DATABASE_URL)
    return db


def test_insert(get_db):
    db = get_db
    assert isinstance(db.select(table_name='urls', fields_name='*'), list)
