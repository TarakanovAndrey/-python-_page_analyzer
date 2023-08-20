import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db():
    with psycopg2.connect('postgres://page_analyzer_base_84ng_user:Sat3BKyF60ZjNqRLg0lyton7w4Voeu03@dpg-cjb32ngcfp5c73a6prk0-a.oregon-postgres.render.com/page_analyzer_base_84ng') as connection:
        try:
            # Подключение к существующей базе данных
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # Курсор для выполнения операций с базой данных
            cursor = connection.cursor()
            cursor.execute('''DROP TABLE IF EXISTS test_urls CASCADE;''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS test_urls (
                            id bigint primary key generated always as identity,
                            name varchar(255) UNIQUE,
                            created_at timestamp DEFAULT CURRENT_TIMESTAMP
                            );''')
            cursor.execute('''DROP TABLE IF EXISTS test_url_checks CASCADE;''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS test_url_checks (
                            id bigint primary key generated always as identity,
                            url_id bigint REFERENCES urls (id),
                            status_code varchar(255), h1 text, title text,
                            description text, created_at timestamp DEFAULT CURRENT_TIMESTAMP
                            );''')
            return 'Create database success!'
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)


if __name__ == '__main__':
    create_db()
