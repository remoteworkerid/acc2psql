import sys

import pyodbc
path = 'D:\Code\equin-django\db\equin.mdb'
conn = pyodbc.connect(f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={path};')
cursor = conn.cursor()

psql = ''
tables = []

for t in cursor.tables():
    tables.append(t.table_name)

table_column_count={}
drop_tables = ''
for t in tables:
    if not 'MSys' in t and not '~TMP' in t:
        print(t)

        count_stat = 0
        foreign_keys = ''
        for st in cursor.statistics(t):
            count_stat = count_stat + 1
            print(st)
            # ke [2] pasti mulai informasi foreign key
            # jika st[5] ada karakter "_" makd dicek. jika yang pertama adalah id, maka itu berarti foreign key one to many, dimana tabelnya ada di bagian kedua. That's it!
            if count_stat >= 3:
                c0 = str(st[2])
                c5 = st[8]
                c1 = str(c5).split('_')[0]
                c2 = str(c5).split('_')[1]

                # it is foreign key!
                if c1 == 'id':
                    foreign_keys = f'{foreign_keys} FOREIGN KEY ({c1}{c2}) REFERENCES {c2} ({c1}{c2}),'

        foreign_keys = foreign_keys[:-1]

        columns = ''
        column_count = 0
        for c in cursor.columns(table=t):
            column_count = column_count + 1
            type = c[5]
            if c[5] == 'COUNTER':
                type = 'SERIAL PRIMARY KEY'
            elif c[5] == 'VARCHAR':
                type = f'VARCHAR({c[6]})'

            columns = f'{columns} {c.column_name} {type},'
        table_column_count[t] = column_count
        columns = columns[:-1]

        if foreign_keys is not '':
            foreign_keys = f', {foreign_keys}'

        drop_tables = f'{drop_tables}DROP TABLE IF EXISTS {t};\n'
        psql = f'{psql}' \
               f'CREATE TABLE {t} (' \
               f'{columns}' \
               f'{foreign_keys}' \
               f');\n'

psql = f'{drop_tables}\n{psql}'
print(psql)