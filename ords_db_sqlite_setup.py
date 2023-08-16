#!/usr/bin/env python3

from funcs import *
import pandas as pd
import sqlite3

logger = logfuncs.init_logger(__file__)

# Creates and populates SQLITE3 tables with ORDS data.


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def sqlite_connect():
    con = False
    try:
        con = sqlite3.connect('ords_test')
        con.row_factory = dict_factory
    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        return con


def log_tables():
    try:
        table_cats = envfuncs.get_var('ORDS_CATS')
        table_data = envfuncs.get_var('ORDS_DATA')
        con = sqlite_connect()
        sql_tbl = """SELECT name, sql FROM sqlite_master WHERE type='table' AND name='{}' ORDER BY name"""
        sql_idx = """SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{}' ORDER BY tbl_name"""
        for row in con.execute(sql_tbl.format(table_cats)):
            logger.debug(row['sql'])
        for row in con.execute(sql_idx.format(table_cats)):
            logger.debug(row['sql'])
        for row in con.execute(sql_tbl.format(table_data)):
            logger.debug(row['sql'])
        for row in con.execute(sql_idx.format(table_data)):
            logger.debug(row['sql'])
        print('See logfile for table structures')
    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        if (con):
            con.close()


def drop_tables():
    try:
        con = sqlite_connect()
        con.execute("DROP TABLE IF EXISTS `{}`".format(
            envfuncs.get_var('ORDS_CATS')))
        con.execute("DROP TABLE IF EXISTS `{}`".format(
            envfuncs.get_var('ORDS_DATA')))
        con.commit()
    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        if (con):
            con.close()


def put_table_categories(schemas):
    table = envfuncs.get_var('ORDS_CATS')
    indices = ['product_category']
    put_table(table, schemas[table]['sql'], indices, 'cat')


def put_table_data(schemas):
    table = envfuncs.get_var('ORDS_DATA')
    indices = ['product_category',
               'product_category_id',
               'data_provider',
               'product_age',
               'repair_status',
               'repair_barrier_if_end_of_life',
               'event_date']
    put_table(table, schemas[table]['sql'], indices, 'dat')


def put_table(table, sql, indices, prefix):
    try:
        con = sqlite_connect()
        con.execute(sql)
        for idx in indices:
            con.execute(
                "CREATE INDEX `{2}_{1}` ON `{0}` (`{1}`)".format(table, idx, prefix))
        con.commit()
        path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table + '.csv'])
        logger.debug('Reading file "{}"'.format(path))
        df = pd.read_csv(path)
        vals = list(zip(*[df[col] for col in df]))
        sql = "INSERT INTO `{}`({}) VALUES({})".format(table, ", ".join(
            df.columns), ",".join(["?"] * len(df.columns)))
        logger.debug(sql)
        with con:
            con.executemany(sql, vals)
        rows = con.total_changes
        logger.debug('{} rows written to table "{}"'.format(rows, table))
        for row in con.execute("SELECT * FROM `{}` LIMIT 1".format(table)):
            print(row)
    except sqlite3.Error as error:
        print("Exception: {}".format(table))
        print(error)
    finally:
        if (con):
            con.close()


def get_schemas():
    schemas = dbfuncs.table_schemas()
    for name, stru in schemas.items():
        sql = """ CREATE TABLE `{}` (""".format(name)
        for field in stru['fields']:
            if field['type'] == 'string':
                if field['name'] != 'problem':
                    sql += "\n`{}` varchar(255),".format(field['name'])
                elif field['name'] == 'problem':
                    sql += "\n`{}` text(255),".format(field['name'])
            elif field['type'] == 'integer':
                sql += "\n`{}` integer,".format(field['name'])
            elif field['type'] == 'number':
                sql += "\n`{}` real,".format(field['name'])
            elif field['type'] == 'date':
                sql += "\n`{}` varchar(10),".format(field['name'])
        sql += """\nPRIMARY KEY (`{}`) );""".format(stru['pkey'])
        schemas[name]['sql'] = sql
    return schemas


schemas = get_schemas()
drop_tables()
log_tables()
put_table_categories(schemas)
put_table_data(schemas)
log_tables()
