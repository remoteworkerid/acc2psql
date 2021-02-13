import sys

import pyodbc
path = 'D:\Code\equin-django\db\equin.accdb'
conn = pyodbc.connect(f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={path};')
cursor = conn.cursor()

psql = ''
tables = []

for t in cursor.tables():
    tables.append(t.table_name)

table_column_count={}
drop_tables = ''
create_tables = {}
for t in tables:
    if not 'MSys' in t and not '~TMP' in t and not 'qry_' in t:# and t == 'transaksisaham':
        # print(t)

        count_stat = 0
        foreign_keys = ''
        foreign_keys_exist = {}
        for st in cursor.statistics(t):
            count_stat = count_stat + 1
            # print(st)
            # ke [2] pasti mulai informasi foreign key
            # jika st[5] ada karakter "_" makd dicek. jika yang pertama adalah id, maka itu berarti foreign key one to many, dimana tabelnya ada di bagian kedua. That's it!
            if count_stat >= 3:
                # print('x', st[8])
                c0 = str(st[2])
                c5 = st[8]
                # print('x', str(c5).split('_'))
                c1 = str(c5).split('_')[0]
                c2 = str(c5).split('_')[1]

                # it is foreign key!
                if c1 == 'id' and foreign_keys_exist.get(c5, None) is None:
                    foreign_keys_exist[c5] = True
                    foreign_keys = f'{foreign_keys}FOREIGN KEY ({c5}) REFERENCES {c2} ({c1}{c2}),\n'

        foreign_keys = foreign_keys[:-2]

        columns = ''
        column_count = 0
        for c in cursor.columns(table=t):
            column_count = column_count + 1
            type = c[5]
            if c[5] == 'COUNTER':
                type = 'SERIAL PRIMARY KEY'
            elif c[5] == 'VARCHAR':
                type = f'VARCHAR({c[6]})'
            elif c[5] == 'DATETIME':
                type = 'TIMESTAMP'
            elif c[5] == 'BIT':
                type = 'BOOLEAN'

            columns = f'{columns} {c.column_name} {type},\n'
        columns = columns[:-2]

        table_column_count[t] = column_count

        if foreign_keys is not '':
            foreign_keys = f'\n, {foreign_keys}'

        drop_tables = f'{drop_tables}DROP TABLE IF EXISTS {t};\n'
        create_sql = f'CREATE TABLE {t} (\n' \
               f'{columns}\n' \
               f'{foreign_keys}\n' \
               f');\n'
        create_tables[t] = create_sql


#SQL Generations
psql = drop_tables
for k in create_tables:
    # print(k)
    psql = f'{psql}\n{create_tables[k]}'
print(psql)