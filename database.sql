db.create_table(table_name='urls', datas_structure=('id bigint primary key generated always as identity',
                                                    'name varchar(255) unique', 'created_at date CURRENT_DATE'))


db.create_table(table_name='url_checks', datas_structure=('id bigint primary key generated always as identity',
                                                          'url_id bigint REFERENCES urls (id)',
                                                          'status_code varchar(255)', 'h1 text', 'title text',
                                                          'description text', 'created_at date CURRENT_DATE'))


db.create_table(table_name='url_last_checks', datas_structure=('id bigint primary key generated always as identity',
                                                          'url_id bigint REFERENCES urls (id)',
                                                          'status_code varchar(255)', 'created_at date'))