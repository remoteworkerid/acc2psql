import sys

import pyodbc
path = 'D:\Code\equin-django\django-equin-2000.mdb'
conn = pyodbc.connect(f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={path};')
cursor = conn.cursor()

psql = ''
tables = []

for t in cursor.tables():
    tables.append(t.table_name)

table_column_count={}

for t in tables:
    if not 'MSys' in t and not '~TMP' in t:

        columns = ''
        column_count = 0
        for c in cursor.columns(table=t):
            column_count = column_count + 1
            # print(c)
            type = c[5]
            if c[5] == 'COUNTER':
                type = 'SERIAL PRIMARY KEY'
            elif c[5] == 'VARCHAR':
                type = f'VARCHAR({c[6]})'

            columns = f'{columns} {c.column_name} {type},'
        table_column_count[t] = column_count
        columns = columns[:-1]

        # print(columns)
        print(f'stats of {t}')
        for st in cursor.statistics(t):
            print('x', st)

        print('-----')
        psql = f'{psql}' \
               f'DROP TABLE IF EXISTS {t};\n' \
               f'CREATE TABLE {t} (' \
               f'{columns}' \
               f');\n'


print(psql)