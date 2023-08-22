import psycopg2
from psycopg2 import Error, extras


class PostgresqlOperations:

    def __init__(self, db_url):
        self.__db_url = db_url

    def url_checks_insert_result(self, id, checks_result):
        url_id = id
        status_code = checks_result['status_code']
        h1 = checks_result['h1']
        title = checks_result['title']
        description = checks_result['description']

        query = (f'''INSERT INTO url_checks (url_id, status_code, h1, title, description)
                VALUES ({url_id}, {status_code}, '{h1}', '{title}', '{description}');''')

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def urls_insert_url(self, url):

        query = f"INSERT INTO urls (name) VALUES ('{url}') ON CONFLICT (name) DO NOTHING;"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def urls_get_id(self, url):

        query = f"SELECT id FROM urls WHERE name='{url}'"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute(query)
                return cursor.fetchone()['id']
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def urls_get_urls_info(self, id_note):

        query = f"SELECT id, name, DATE(created_at) FROM urls WHERE id='{id_note}'"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute(query)
                return cursor.fetchone()
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def urls_get_url(self, id_note):

        query = f"SELECT name FROM urls WHERE id='{id_note}'"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute(query)
                return cursor.fetchone()['name']
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def url_checks_get_checks_info(self, id_note):

        query = f'''SELECT id, status_code, h1, title, description, DATE(created_at)
                FROM url_checks
                WHERE url_id='{id_note}'
                ORDER BY id DESC'''

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute(query)
                return cursor.fetchall()
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def selecting_summary_information(self):
        query = '''SELECT urls.id, urls.name, url_checks.status_code, DATE(url_checks.created_at)
                    FROM urls
                    LEFT OUTER JOIN url_checks
                    ON urls.id = url_checks.url_id
                    WHERE url_checks.created_at = (SELECT MAX(created_at)
                    FROM url_checks WHERE urls.id = url_checks.url_id)
                    OR url_checks.created_at IS NULL ORDER BY urls.id DESC;'''
        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor(cursor_factory=extras.DictCursor)
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def check_urls_exist(self, url: str):

        query = f"SELECT EXISTS (SELECT name FROM urls WHERE name='{url}');"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)
                rows = cursor.fetchone()
                return rows[0]
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)
