#!/usr/bin/env python3

import pandas as pd
from funcs import *
import sqlite3
from sqlite3 import Error

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
    except Exception as error:
        print("Exception: {}".format(error))
    finally:
        return con


def show_tables():
    try:
        con = sqlite_connect()
        for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            print(row)
            logger.debug(row)
    except Exception as error:
        print("Exception: {}".format(error))
    finally:
        if (con):
            con.close()


def drop_tables():
    try:
        con = sqlite_connect()
        table_cats = envfuncs.get_var('ORDS_CATS')
        con.execute("DROP TABLE IF EXISTS `{}`".format(table_cats))
        table_data = envfuncs.get_var('ORDS_DATA')
        con.execute("DROP TABLE IF EXISTS `{}`".format(table_data))
        con.commit()
        show_tables()
    except Exception as error:
        print("Exception: {}".format(error))
    finally:
        if (con):
            con.close()


def put_table_categories():
    try:
        table_cats = envfuncs.get_var('ORDS_CATS')
        con = sqlite_connect()
        con.execute("CREATE TABLE `{}`(product_category_id integer primary key, product_category varchar (64))".format(table_cats))
        con.execute("CREATE INDEX `product_category` ON `{}` (`product_category`)".format(table_cats))
        con.commit()
        path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table_cats + '.csv'])
        logger.debug('Reading file "{}"'.format(path))
        dfcats = pd.read_csv(path)
        vals = list(zip(*[dfcats[col] for col in dfcats]))
        sql = "INSERT INTO `{}`(product_category_id, product_category) VALUES(?, ?)".format(table_cats)
        logger.debug(sql)
        with con:
            con.executemany(sql, vals)
        rows = con.total_changes
        logger.debug('{} rows written to table "{}"'.format(rows, table_cats))
        for row in con.execute("SELECT * FROM `{}`".format(table_cats)):
            print(row)

    except Exception as error:
        print("Exception: {}".format(error))
    finally:
        show_tables()
        if (con):
            con.close()


def put_table_data():
    table_data = envfuncs.get_var('ORDS_DATA')
    try:
        con = sqlite_connect()
        sql = """
        CREATE TABLE `{}` (
        `id` varchar(32) PRIMARY KEY,
        `data_provider` varchar(32),
        `country` varchar(3),
        `partner_product_category` varchar(255),
        `product_category` varchar(64),
        `product_category_id` integer,
        `brand` varchar(128),
        `year_of_manufacture` varchar(4),
        `product_age` varchar(6),
        `repair_status` varchar(16),
        `repair_barrier_if_end_of_life` varchar(32),
        `group_identifier` varchar(64),
        `event_date` varchar(10),
        `problem` text(255)
        )
        """.format(table_data)
        con.execute(sql)
        con.execute("CREATE INDEX `product_category_1` ON `{}` (`product_category`)".format(table_data))
        con.execute("CREATE INDEX `product_category_id_1` ON `{}` (`product_category_id`)".format(table_data))
        con.execute("CREATE INDEX `data_provider` ON `{}` (`data_provider`)".format(table_data))
        con.execute("CREATE INDEX `product_age` ON `{}` (`product_age`)".format(table_data))
        con.execute("CREATE INDEX `repair_status` ON `{}` (`repair_status`)".format(table_data))
        con.execute("CREATE INDEX `repair_barrier_if_end_of_life` ON `{}` (`repair_barrier_if_end_of_life`)".format(table_data))
        con.execute("CREATE INDEX `event_date`ON `{}` (`event_date`)".format(table_data))
        con.execute("CREATE INDEX `problem`ON `{}` (`problem`)".format(table_data))
        con.commit()
        path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table_data + '.csv'])
        logger.debug('Reading file "{}"'.format(path))
        dfdata = pd.read_csv(path)
        vals = list(zip(*[dfdata[col] for col in dfdata]))
        sql = "INSERT INTO `{}`({}) VALUES({})".format(table_data, ", ".join(dfdata.columns), ",".join(["?"] * len(dfdata.columns)))
        logger.debug(sql)
        with con:
            con.executemany(sql, vals)
        rows = con.total_changes
        logger.debug('{} rows written to table "{}"'.format(rows, table_data))
        for row in con.execute("SELECT * FROM `{}` LIMIT 1".format(table_data)):
            print(row)
            break

    except Exception as error:
        print("Exception: {}".format(error))
    finally:
        show_tables()
        if (con):
            con.close()


drop_tables()
put_table_categories()
put_table_data()
