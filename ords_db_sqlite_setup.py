#!/usr/bin/env python3


# Creates and populates SQLITE3 tables with ORDS data.

import sqlite3
from funcs import *


def sqlite_connect():
    con = False
    try:
        con = dbfuncs.sqlite_connection()
    except sqlite3.Error as error:
        print(f"Exception: {error}")
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
            print(f"See logfile for table structure: {table_cats}")
        else:
            print(f"Table not found: {table_cats}")

        count = con.execute(sql_count.format(table_data)).fetchone()
        if count["records"] > 0:
            for row in con.execute(sql_idx.format(table_data)):
                logger.debug(row["sql"])
            for row in con.execute(sql_idx.format(table_data)):
                logger.debug(row["sql"])
            print(f"See logfile for table structure: {table_data}")
        else:
            print(f"Table not found: {table_data}")

    except sqlite3.Error as error:
        print(f"Exception: {error}")
    finally:
        if con:
            con.close()


def drop_table(table):
    try:
        con = sqlite_connect()
        con.execute(f"DROP TABLE IF EXISTS `{table}`")
        con.commit()
    except sqlite3.Error as error:
        print(f"Exception: {error}")
    finally:
        if con:
            con.close()


def put_table(table, sql, indices, prefix):
    try:
        con = sqlite_connect()
        con.execute(sql)
        for idx in indices:
            con.execute(f"CREATE INDEX `{prefix}_{idx}` ON `{table}` (`{idx}`)")
        con.commit()
    except sqlite3.Error as error:
        print(f"Exception: {table}")
        print(error)
    finally:
        if con:
            con.close()


def import_data(tablename, df):
    try:
        con = sqlite_connect()
        logger.debug(f'{len(df)} rows to write to table "{tablename}"')
        vals = list(df.to_numpy())
        sql = "INSERT INTO `{}`({}) VALUES({})".format(
            tablename, ", ".join(df.columns), ",".join(["?"] * len(df.columns))
        )
        logger.debug(sql)
        con.executemany(sql, vals)
        rows = con.total_changes
        logger.debug(f'{rows} rows written to table "{tablename}"')
        for row in con.execute(f"SELECT * FROM `{tablename}` LIMIT 1"):
            print(row)
    except sqlite3.Error as error:
        print(f"Exception: {tablename}")
        print(error)
    finally:
        if con:
            con.close()


def get_schemas():
    schemas = ordsfuncs.table_schemas()
    for name, stru in schemas.items():
        sql = f" CREATE TABLE `{name}` ("
        for field in stru["fields"]:
            fieldname = field["name"]
            fieldtype = field["type"]
            if fieldtype == "string":
                if fieldname != "problem":
                    sql += f"\n`{fieldname}` varchar(255),"
                elif fieldname == "problem":
                    sql += f"\n`{fieldname}` text(255),"
            elif fieldtype == "integer":
                sql += f"\n`{fieldname}` integer,"
            elif fieldtype == "number":
                sql += f"\n`{fieldname}` real,"
            elif fieldtype == "date":
                sql += f"\n`{fieldname}` varchar(10),"
        sql += f"\nPRIMARY KEY (`{stru['pkey']}`) );"
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
        print(f"Exception: {error}")


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dbfuncs.dbvars = cfg.get_dbvars()

    table_cats = cfg.get_envvar("ORDS_CATS")
    table_data = cfg.get_envvar("ORDS_DATA")

    drop_table(table_cats)
    drop_table(table_data)
    create_from_schema()
    import_data(table_cats, ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS")))
    import_data(table_data, ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")))
