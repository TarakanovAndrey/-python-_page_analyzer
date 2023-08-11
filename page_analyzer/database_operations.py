import psycopg2


# class PostgresqlDBManagementSystem(object):
#     """Питоновский класс для баловства с postgresql"""
#
#     __instance = None
#     __host = None
#     __user = None
#     __password = None
#     __database = None
#     __cursor = None
#     __connection = None
#
#     # def __new__(cls, *args, **kwargs):
#     #     if not cls.__instance or not cls.__database:
#     #         cls.__instance = super(PostgresqlDBManagementSystem, cls).__new__(cls, *args, **kwargs)
#     #     return cls.__instance
#
#     def __init__(self, host='localhost', user='nester', password='', database=''):
#         self.__host = host
#         self.__user = user
#         self.__password = password
#         self.__database = database
#
#     def __open(self):
#         self.__connection = psycopg2.connect("dbname='{0}' user='{1}'".format(self.__database, self.__user))
#         self.__cursor = self.__connection.cursor()
#         # try:
#         #     self.__connection = psycopg2.connect("dbname='{0}' user='{1}'".format(self.__database, self.__user))
#         #     self.__cursor = self.__connection.cursor()
#
#         # except:
#         # except psycopg2.DatabaseError, e:
#         #     if self.__connection:
#         #         self.__connection.rollback()
#         #     print( 'Error %s %e')
#         #     sys.exit(1)
#
#     def __close(self):
#         self.__connection.close()
#
#     def create_table(self, table_name, table_structure):
#
#         query = "CREATE TABLE " + table_name + table_structure
#         self.__open()
#         self.__cursor.execute("DROP TABLE IF EXISTS {0}".format(table_name))
#         self.__cursor.execute(query)
#         self.__connection.commit()
#         self.__close()
#


#############################################################################
def datas_to_dict(keys, values):
    keys = tuple(x[0] for x in keys)
    result = []
    for item in values:
        dict_ = {}
        for key, value in zip(keys, item):
            dict_[key] = value
        result.append(dict_)
    return result


class PostgresqlOperations:

    __instance = None
    __host = None
    __user = None
    __password = None
    __database = None
    __cursor = None
    __connection = None

    def __init__(self, host='localhost',
                 user='nester',
                 password='',
                 database=''):

        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database

    def __open(self):
        try:
            self.__connection = psycopg2.connect(database=self.__database,
                                                 user=self.__user,
                                                 password=self.__password)
            self.__cursor = self.__connection.cursor()

        except psycopg2.DatabaseError:
            print("Can't establish connection to database")
            '''Прописать откат любых изменений в случае ошибки подключения. rollback'''

    def __close(self):
        self.__connection.close()

    def create_table(self, table_name, datas_structure):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(datas_structure)});"

        self.__open()
        self.__cursor.execute(query)

        self.__connection.commit()
        self.__close()

    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.__open()
        self.__cursor.execute(query)
        self.__connection.commit()
        self.__close()

    def delete(self, table,
               where: str = False):

        """
        Реализуется запрос формата
        DELETE FROM <НАЗВАНИЕ ТАБЛИЦЫ> WHERE <УСЛОВИЕ ПО КОТОРОМУ УДАЛЯЕТСЯ СТРОКА ИЛИ СТРОКИ>
        """
        delete = f"DELETE FROM {table}"
        where = f"WHERE {where}" if where else False
        queries_body = (delete, where)
        query = ' '.join(filter(lambda x: bool(x), queries_body)) + ';'
        print(query)
        self.__open()
        self.__cursor.execute(query)

        self.__connection.commit()
        self.__close()

    def insert(self, *args, **kwargs):
        table_name = args[0]
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f"INSERT INTO {table_name} ({fields_name}) VALUES ({values})"
        print(query)
        self.__open()
        self.__cursor.execute(query)
        self.__connection.commit()
        self.__close()

    def insert_unique(self, *args, **kwargs):
        table_name = args[0]
        fields_name = ', '.join(kwargs.keys())
        values = ', '.join(f"'{x}'" for x in kwargs.values())

        query = f"INSERT INTO {table_name} ({fields_name}) VALUES ({values}) ON CONFLICT (name) DO NOTHING;"

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
               fields_name: str = None,
               condition: str = None,
               fields_order: str = None,
               order: str = None,
               fetch: str = 'all'):

        """
         Реализован запрос вида: SELECT <fields_name> FROM <table_name> WHERE <condition> ORDER BY <fields_order>
         <order>
        :param table_name: название таблицы
        :param fields_name: название полей, данные по которым надо вывести. Перечисляются в кавычках через запятую
        :param condition: условаия выборки данных в кавычках через запятую
        :param fields_order: поле по которому упорядочивается
        :param order: порядок вывода данных DESC - в обратном порядке. Если ничего не указывать, то по умолчанию
                выводится в прямом
        :param fetch: если указать 'one', то возьмется верхняя строка из таблицы. По умолчанию выводятся все
        :return: возвращается словарь, если одна строка или если требуется из всех строк вывести только строку с
                последней проверкой, и список словарей, если больше одной строки
        """

        query_body = f"SELECT {fields_name} FROM {table_name}"
        condition = f"WHERE {condition}" if condition else False
        order = f"ORDER BY {fields_order} {order}" if fields_order else False
        query_items = (query_body, condition, order)
        query = ' '.join(item for item in query_items if item) + ';'

        self.__open()
        self.__cursor.execute(query)

        rows = self.__cursor.fetchall()

        self.__connection.commit()
        self.__close()
        if len(rows) == 1 and fetch == 'all' or len(rows) > 1 and fetch == 'one':
            return datas_to_dict(self.get_heads_table(table_name), rows)[0]

        return datas_to_dict(self.get_heads_table(table_name), rows)

    def update(self, table,
               field_name,
               condition: str = False):
        """
        Реализуется запрос вида
        UPDATE <ИМЯ ТАБЛИЦЫ> SET <НА КАКОЕ ЗНАЧЕНИЕ В КАКОМ ПОЛЕ МЕНЯЕТСЯ> WHERE <УСЛОВИЕ КАКИЕ ПОЛЯ ОТБИРАЮТСЯ
        ДЛЯ ЗАМЕНЫ>
        """
        update = f"UPDATE {table}"
        set_ = f"SET {field_name}"
        condition = f"WHERE {condition}" if condition else False
        queries_body = (update, set_, condition)
        query = ' '.join(filter(lambda x: bool(x), queries_body)) + ';'
        # print(query)
        self.__open()
        self.__cursor.execute(query)

        self.__connection.commit()
        self.__close()


# db = PostgresqlOperations(user='andrey', password='password', database='database')
#
# # db.create_table(table_name='sites_list', datas_structure=(('id bigint primary key generated always as identity'),
# #                                                      ('name varchar(255) unique'),
# #                                                      ('created_at date'))
# #                 )
# #
# db.create_table(table_name='checks_info', datas_structure=(('id bigint primary key generated always as identity'),
#                                                            ('sites_list_id bigint REFERENCES sites_list (id)'),
#                                                            ('code_response varchar(255)'),
#                                                            ('h1 text'),
#                                                            ('title text'),
#                                                            ('description text'),
#                                                            ('created_at date')))

# значение по умолчанию "" чтобы при добавлении ячеек не было none
