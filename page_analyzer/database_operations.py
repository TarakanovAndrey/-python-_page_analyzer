import psycopg2


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
    __cursor = None
    __connection = None
    __instance = None
    __database = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance or not cls.__database:
            cls.__instance = super(PostgresqlOperations, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, db_url):
        self.__db_url = db_url

    def __open(self):
        try:
            self.__connection = psycopg2.connect(self.__db_url)
            self.__cursor = self.__connection.cursor()

        except psycopg2.DatabaseError:
            print("Can't establish connection to database")
            '''Прописать откат любых изменений в случае ошибки подключения. rollback'''

    def __close(self):
        self.__connection.close()

    def insert(self, *args, **kwargs):
        table_name = args[0]
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f"INSERT INTO {table_name} ({fields_name}) VALUES ({values}) RETURNING id;"

        self.__open()
        self.__cursor.execute(query)

        self.__connection.commit()
        self.__close()

    def insert_unique(self, *args, **kwargs):
        table_name = args[0]
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f'''INSERT INTO {table_name} ({fields_name})
                    VALUES ({values}) ON CONFLICT (name) DO NOTHING;'''

        self.__open()
        self.__cursor.execute(query)

        self.__connection.commit()
        self.__close()

    def get_heads_table(self, table_name):
        """Вывод названия всех полей таблицы"""
        table_name = table_name
        query = (f"SELECT column_name "
                 f"FROM information_schema.columns "
                 f"WHERE table_schema = 'public' "
                 f"AND table_name = '{table_name}' ORDER BY ordinal_position ASC")

        self.__open()
        self.__cursor.execute(query)
        rows = self.__cursor.fetchall()
        self.__connection.commit()
        self.__close()
        return rows

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

        self.__open()
        self.__cursor.execute(query)

        if fetch == 'one':
            rows = self.__cursor.fetchone()
        else:
            rows = self.__cursor.fetchall()

        self.__connection.commit()
        self.__close()

        if fields_name == '*':
            column_name = tuple([x[0] for x in self.get_heads_table(table_name='urls')])
        else:
            column_name = fields_name
        out = datas_to_dict({'column_name': column_name, 'rows': rows})

        return out

    def select_special(self):
        query = '''SELECT urls.id, urls.name, url_checks.status_code, DATE(url_checks.created_at)
                    FROM urls
                    LEFT OUTER JOIN url_checks
                    ON urls.id = url_checks.url_id
                    WHERE url_checks.created_at = (SELECT MAX(created_at)
                    FROM url_checks WHERE urls.id = url_checks.url_id)
                    OR url_checks.created_at IS NULL ORDER BY urls.id DESC;'''
        self.__open()
        self.__cursor.execute(query)
        rows = self.__cursor.fetchall()

        self.__connection.commit()
        self.__close()
        column_name = ('id', 'name', 'status_code_last_check', 'created_at_last_check')
        out = datas_to_dict({'column_name': column_name, 'rows': rows})
        return out

    def check_exists(self, table_name: str,
                     fields_name: (tuple, str) = None,
                     condition: str = None):

        query = f"SELECT EXISTS (SELECT {fields_name} FROM {table_name} WHERE {condition});"
        print(query)

        self.__open()
        self.__cursor.execute(query)
        print(self.__cursor.execute(query))
        rows = self.__cursor.fetchall()
        self.__connection.commit()
        self.__close()

        return {'answer': rows[0][0]}



