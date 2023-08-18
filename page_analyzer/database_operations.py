import psycopg2
from psycopg2 import Error


def datas_to_dict(items):
    keys = items['column_name']
    values = items['rows']
    rows = list()
    for item in values:
        dict_ = {}
        for key, value in zip(keys, item):
            if value is None:
                value = ''
                dict_[key] = value
            dict_[key] = value
        rows.append(dict_)

    return tuple(rows)


class PostgresqlOperations:

    def __init__(self, db_url):
        self.__db_url = db_url

    def insert(self, *args, **kwargs):
        table_name = args[0]
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f"INSERT INTO {table_name} ({fields_name}) VALUES ({values}) RETURNING id;"

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def insert_unique(self, *args, **kwargs):
        table_name = args[0]
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

    def get_heads_table(self, table_name):
        """Вывод названия всех полей таблицы"""
        table_name = table_name
        query = (f"SELECT column_name "
                 f"FROM information_schema.columns "
                 f"WHERE table_schema = 'public' "
                 f"AND table_name = '{table_name}' ORDER BY ordinal_position ASC")

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows

            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def select(self, table_name: str,
               fields_name: (tuple, str) = None,
               condition: str = None,
               fields_order: str = None,
               order: str = None,
               fetch: str = 'all',
               group: str = False):

        """
         Реализован запрос вида: SELECT <fields_name> FROM <table_name> WHERE <condition> ORDER BY <fields_order>
         <order>
        :param group:
        :param table_name: название таблицы
        :param fields_name: название полей, данные по которым надо вывести. Кортеж, перечисляются в
         кавычках через запятую
        :param condition: условаия выборки данных в кавычках через запятую
        :param fields_order: поле по которому упорядочивается
        :param order: порядок вывода данных DESC - в обратном порядке. Если ничего не указывать, то по умолчанию
                выводится в прямом
        :param fetch: если указать 'one', то возьмется верхняя строка из таблицы. По умолчанию выводятся все
        :return: возвращается словарь, если одна строка или если требуется из всех строк вывести только строку с
                последней проверкой, и список словарей, если больше одной строки
        """

        query_body = f"SELECT {', '.join(fields_name)} FROM {table_name}"
        condition = f"WHERE {condition}" if condition else False
        order = f"ORDER BY {fields_order} {order}" if fields_order else False
        group = f"GROUP BY {group}" if group else False

        query_items = (query_body, condition, order, group)
        query = ' '.join(item for item in query_items if item) + ';'

        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)
                if fetch == 'one':
                    rows = cursor.fetchone()
                else:
                    rows = cursor.fetchall()

                if fields_name == '*':
                    column_name = tuple([x[0] for x in self.get_heads_table(table_name='urls')])
                else:
                    column_name = fields_name
                out = datas_to_dict({'column_name': column_name, 'rows': rows})
                return out

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
                cursor = connect.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                column_name = ('id', 'name', 'status_code_last_check', 'created_at_last_check')
                out = datas_to_dict({'column_name': column_name, 'rows': rows})
                return out
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)

    def check_exists(self, table_name: str,
                     fields_name: (tuple, str) = None,
                     condition: str = None):

        query = f"SELECT EXISTS (SELECT {fields_name} FROM {table_name} WHERE {condition});"
        cursor = self.__connect()
        with psycopg2.connect(self.__db_url) as connect:
            try:
                cursor = connect.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return {'answer': rows[0][0]}
            except (Exception, Error) as error:
                print("Ошибка при работе с Postgresql", error)
