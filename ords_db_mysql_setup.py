#!/usr/bin/env python3

# Creates and populates MYSQL tables with ORDS data.

from funcs import *

def log_tables():
    try:
        row = dbfuncs.mysql_show_create_table(table_cats)
        if row:
            logger.debug(row)
            print(f"See logfile for table structure: {table_cats}")
        else:
            print(f"Table not found: {table_cats}")
        row = dbfuncs.mysql_show_create_table(table_data)
        if row:
            logger.debug(row)
            print(f"See logfile for table structure: {table_data}")
        else:
            print(f"Table not found: {table_data}")
    except Exception as error:
        print(f"Exception: {error}")


def drop_table(table):
    try:
        dbfuncs.mysql_execute(f"DROP TABLE IF EXISTS `{table}`")
    except Exception as error:
        print(f"Exception: {error}")


def put_table(table, sql, indices):
    try:
        dbfuncs.mysql_execute(sql)
        for idx in indices:
            dbfuncs.mysql_execute(f"ALTER TABLE `{table}` ADD KEY (`{idx}`)")
    except Exception as error:
        print("Exception: {table}")
        print(error)


def get_schemas():
    schemas = ordsfuncs.table_schemas()
    for name, stru in schemas.items():
        sql = f" CREATE TABLE `{name}` ("
        for field in stru["fields"]:
            fieldname = field["name"]
            fieldtype = field["type"]
            if fieldtype == "string":
                if fieldname != "problem":
                    sql += f"\n`{fieldname}` varchar(255) DEFAULT NULL,"
                elif fieldname == "problem":
                    sql += f"\n`{fieldname}` text"
            elif fieldtype == "integer":
                sql += f"\n`{fieldname}` int DEFAULT NULL,"
            elif fieldtype == "number":
                sql += f"\n`{fieldname}` float DEFAULT 0,"
            elif fieldtype == "date":
                sql += f"\n`{fieldname}` varchar(10) DEFAULT NULL,"
        sql = (
            sql.strip(",")
            + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        )
        sql += f"\nALTER TABLE `{name}` ADD PRIMARY KEY (`{stru['pkey']}`);"
        schemas[name]["sql"] = sql
    return schemas


def import_data(tablename, df):

    logger.debug(f"{len(df)} rows to write to table {tablename}")
    rows = df.to_pandas(use_pyarrow_extension_array=True).to_sql(
        name=tablename, con=dbfuncs.alchemy_eng(), if_exists="append", index=False
    )

    logger.debug(f"{rows} rows written to table {tablename}")
    for row in dbfuncs.mysql_query_fetchall(f"SELECT * FROM `{tablename}` LIMIT 1"):
        print(row)


# 'json' to create tables using ./dat/ords/tableschema.json
# If preferred, import 'sql' from ./dat/tableschema_ords_mysql.sql.
# SQL structure gives more fine-grained column sizes, data types may differ though.
# SQL file not guaranteed to always reflect correct schema or to exist in the future.
def create_from_schema(schema="sql"):

    try:
        log_tables()
        if schema == "json":
            drop_table(table_cats)
            drop_table(table_data)
            schemas = get_schemas()
            # Categories table
            logger.debug(schemas[table_cats]["sql"])
            put_table(table_cats, schemas[table_cats]["sql"], ["product_category"])
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
            put_table(table_data, schemas[table_data]["sql"], indices)
            dbfuncs.mysql_execute(
                f"ALTER TABLE `{table_data}` ADD FULLTEXT KEY (`problem`)"
            )
        elif schema == "sql":
            path = pathfuncs.get_path(
                [cfg.DATA_DIR, "tableschema_ords_mysql.sql"]
            )
            logger.debug(f"Reading file {path}")
            sql = path.read_text().format(table_cats, table_data)
            logger.debug(sql)
            dbfuncs.mysql_execute_multi(sql)
        log_tables()
    except Exception as error:
        print(f"Exception: {error}")


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dbfuncs.dbvars = cfg.get_dbvars()

    table_cats = cfg.get_envvar("ORDS_CATS")
    table_data = cfg.get_envvar("ORDS_DATA")

    create_from_schema()
    import_data(table_cats, ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS")))
    import_data(table_data, ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")))
