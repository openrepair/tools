#!/usr/bin/env python3


# Creates and populates SQLITE3 tables with ORDS data.

from funcs import *
import pandas as pd
import sqlite3


def sqlite_connect():
    con = False
    try:
        con = dbfuncs.sqlite_connect()
    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        return con


def log_tables():
    try:
        con = sqlite_connect()
        sql_count = """SELECT COUNT(*) as records FROM sqlite_master WHERE type='table' AND name='{}' ORDER BY name"""
        sql_tbl = """SELECT name, sql FROM sqlite_master WHERE type='table' AND name='{}' ORDER BY name"""
        sql_idx = """SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{}' ORDER BY tbl_name"""
        count = con.execute(sql_count.format(table_cats)).fetchone()
        if count["records"] > 0:
            for row in con.execute(sql_tbl.format(table_cats)):
                logger.debug(row["sql"])
            for row in con.execute(sql_idx.format(table_cats)):
                logger.debug(row["sql"])
            print("See logfile for table structure: {}".format(table_cats))
        else:
            print("Table not found: {}".format(table_cats))

        count = con.execute(sql_count.format(table_data)).fetchone()
        if count["records"] > 0:
            for row in con.execute(sql_idx.format(table_data)):
                logger.debug(row["sql"])
            for row in con.execute(sql_idx.format(table_data)):
                logger.debug(row["sql"])
            print("See logfile for table structure: {}".format(table_data))
        else:
            print("Table not found: {}".format(table_data))

    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        if con:
            con.close()


def drop_table(table):
    try:
        con = sqlite_connect()
        con.execute("DROP TABLE IF EXISTS `{}`".format(table))
        con.commit()
    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        if con:
            con.close()


def put_table(table, sql, indices, prefix):
    try:
        con = sqlite_connect()
        con.execute(sql)
        for idx in indices:
            con.execute(
                "CREATE INDEX `{2}_{1}` ON `{0}` (`{1}`)".format(table, idx, prefix)
            )
        con.commit()
    except sqlite3.Error as error:
        print("Exception: {}".format(table))
        print(error)
    finally:
        if con:
            con.close()


def import_data(table):
    try:
        con = sqlite_connect()
        path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table + ".csv"])
        logger.debug('Reading file "{}"'.format(path))
        df = pd.read_csv(path)
        logger.debug('{} rows to write to table "{}"'.format(len(df), table))
        vals = list(zip(*[df[col] for col in df]))
        sql = "INSERT INTO `{}`({}) VALUES({})".format(
            table, ", ".join(df.columns), ",".join(["?"] * len(df.columns))
        )
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
        if con:
            con.close()


def get_schemas():
    schemas = dbfuncs.table_schemas()
    for name, stru in schemas.items():
        sql = """ CREATE TABLE `{}` (""".format(name)
        for field in stru["fields"]:
            if field["type"] == "string":
                if field["name"] != "problem":
                    sql += "\n`{}` varchar(255),".format(field["name"])
                elif field["name"] == "problem":
                    sql += "\n`{}` text(255),".format(field["name"])
            elif field["type"] == "integer":
                sql += "\n`{}` integer,".format(field["name"])
            elif field["type"] == "number":
                sql += "\n`{}` real,".format(field["name"])
            elif field["type"] == "date":
                sql += "\n`{}` varchar(10),".format(field["name"])
        sql += """\nPRIMARY KEY (`{}`) );""".format(stru["pkey"])
        schemas[name]["sql"] = sql
    return schemas


def create_from_schema(schema="json"):
    import time

    try:
        time.sleep(3)
        log_tables()
        if schema == "json":
            schemas = get_schemas()
            # Categories table
            logger.debug(schemas[table_cats]["sql"])
            put_table(
                table_cats, schemas[table_cats]["sql"], ["product_category"], "cat"
            )
            # Data table
            indices = [
                "product_category",
                "product_category_id",
                "data_provider",
                "product_age",
                "repair_status",
                "repair_barrier_if_end_of_life",
                "event_date",
            ]
            logger.debug(schemas[table_data]["sql"])
            put_table(table_data, schemas[table_data]["sql"], indices, "dat")
        elif schema == "sql":
            pass
        time.sleep(3)
        log_tables()
    except Exception as error:
        print("Exception: {}".format(error))


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    table_cats = envfuncs.get_var("ORDS_CATS")
    table_data = envfuncs.get_var("ORDS_DATA")

    drop_table(table_cats)
    drop_table(table_data)
    create_from_schema()
    import_data(table_cats)
    import_data(table_data)
