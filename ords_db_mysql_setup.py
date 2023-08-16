#!/usr/bin/env python3

from funcs import *
import pandas as pd

logger = logfuncs.init_logger(__file__)

# Creates and populates MYSQL tables with ORDS data.


def log_tables():
    try:
        row = dbfuncs.show_create_table(envfuncs.get_var('ORDS_CATS'))
        if row:
            logger.debug(row)
        else:
            print("Table not found: {}".format(envfuncs.get_var('ORDS_CATS')))
        row = dbfuncs.show_create_table(envfuncs.get_var('ORDS_DATA'))
        if row:
            logger.debug(row)
        else:
            print("Table not found: {}".format(envfuncs.get_var('ORDS_DATA')))
        return
    except Exception as error:
        print("Exception: {}".format(error))


def drop_tables():
    try:
        dbfuncs.execute("DROP TABLE IF EXISTS `{}`".format(
            envfuncs.get_var('ORDS_CATS')))
        dbfuncs.execute("DROP TABLE IF EXISTS `{}`".format(
            envfuncs.get_var('ORDS_DATA')))
    except Exception as error:
        print("Exception: {}".format(error))


def put_table_categories(schemas):
    table = envfuncs.get_var('ORDS_CATS')
    indices = ['product_category']
    put_table(table, schemas[table]['sql'], indices)


def put_table_data(schemas):
    table = envfuncs.get_var('ORDS_DATA')
    indices = ['product_category',
               'product_category_id',
               'data_provider',
               'product_age',
               'repair_status',
               'repair_barrier_if_end_of_life',
               'event_date']
    put_table(table, schemas[table]['sql'], indices)
    dbfuncs.execute( "ALTER TABLE `{}` ADD FULLTEXT KEY (`problem`)".format(table))


def put_table(table, sql, indices):
    try:
        dbfuncs.execute(sql)
        for idx in indices:
            dbfuncs.execute( "ALTER TABLE `{}` ADD KEY (`{}`)".format(table, idx))
        path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table + '.csv'])
        logger.debug('Reading file "{}"'.format(path))
        df = pd.read_csv(path)
        rows = df.to_sql(name=table, con=dbfuncs.alchemy_eng(),
                            if_exists='append', index=False)
        logger.debug('{} written to table "{}"'.format(rows, table))
        for row in dbfuncs.query_fetchall("SELECT * FROM `{}` LIMIT 1".format(table)):
            print(row)
    except Exception as error:
        print("Exception: {}".format(table))
        print(error)


def get_schemas():
    schemas = dbfuncs.table_schemas()
    for name, stru in schemas.items():
        sql = """ CREATE TABLE `{}` (""".format(name)
        for field in stru['fields']:
            if field['type'] == 'string':
                if field['name'] != 'problem':
                    sql += "\n`{}` varchar(255) DEFAULT NULL,".format(
                        field['name'])
                elif field['name'] == 'problem':
                    sql += "\n`{}` text".format(field['name'])
            elif field['type'] == 'integer':
                sql += "\n`{}` int DEFAULT NULL,".format(field['name'])
            elif field['type'] == 'number':
                sql += "\n`{}` float DEFAULT 0,".format(field['name'])
            elif field['type'] == 'date':
                sql += "\n`{}` varchar(10) DEFAULT NULL,".format(
                    field['name'])
        sql = sql.strip(
            ',') + """\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""
        sql += """\nALTER TABLE `{}` ADD PRIMARY KEY (`{}`);""".format(
            name, stru['pkey'])
        schemas[name]['sql'] = sql
    return schemas


schemas = get_schemas()
drop_tables()
log_tables()
put_table_categories(schemas)
put_table_data(schemas)
log_tables()
