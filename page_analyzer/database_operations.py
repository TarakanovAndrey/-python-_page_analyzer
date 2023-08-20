import psycopg2
from psycopg2 import Error, extras


class PostgresqlOperations:

    def __init__(self, db_url):
        self.__db_url = db_url

    def insert(self, table_name, **kwargs):
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f"INSERT INTO {table_name} ({fields_name}) VALUES ({values}) RETURNING id;"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def insert_unique(self, table_name, **kwargs):
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f'''INSERT INTO {table_name} ({fields_name})
                    VALUES ({values}) ON CONFLICT (name) DO NOTHING;'''

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def select(self, table_name: str,
               fields_name: (tuple, str) = None,
               condition: str = None,
               fields_order: str = None,
               order: str = None,
               fetch: str = 'all',
               group: str = False):

        query_body = f"SELECT {', '.join(fields_name)} FROM {table_name}"
        condition = f"WHERE {condition}" if condition else False
        order = f"ORDER BY {fields_order} {order}" if fields_order else False
        group = f"GROUP BY {group}" if group else False

        query_items = (query_body, condition, order, group)
        query = ' '.join(item for item in query_items if item) + ';'

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute(query)
                if fetch == 'one':
                    rows = cursor.fetchone()
                else:
                    rows = cursor.fetchall()

                return rows
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def select_special(self):
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

    def check_exists(self, table_name: str,
                     fields_name: (tuple, str) = None,
                     condition: str = None):

        query = f"SELECT EXISTS (SELECT {fields_name} FROM {table_name} WHERE {condition});"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return {'answer': rows[0][0]}
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def clear_table(self, table_name):
        query = f"DELETE FROM {table_name};"
        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)
