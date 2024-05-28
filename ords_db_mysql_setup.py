#!/usr/bin/env python3

# Creates and populates MYSQL tables with ORDS data.

from funcs import *

def log_tables():
    try:
        row = dbfuncs.mysql_show_create_table(table_cats)
        if row:
            logger.debug(row)
            print("See logfile for table structure: {}".format(table_cats))
        else:
            print("Table not found: {}".format(table_cats))
        row = dbfuncs.mysql_show_create_table(table_data)
        if row:
            logger.debug(row)
            print("See logfile for table structure: {}".format(table_data))
        else:
            print("Table not found: {}".format(table_data))
    except Exception as error:
        print("Exception: {}".format(error))


def drop_table(table):
    try:
        dbfuncs.mysql_execute("DROP TABLE IF EXISTS `{}`".format(table))
    except Exception as error:
        print("Exception: {}".format(error))


def put_table(table, sql, indices):
    try:
        dbfuncs.mysql_execute(sql)
        for idx in indices:
            dbfuncs.mysql_execute("ALTER TABLE `{}` ADD KEY (`{}`)".format(table, idx))
    except Exception as error:
        print("Exception: {}".format(table))
        print(error)


def get_schemas():
    schemas = ordsfuncs.table_schemas()
    for name, stru in schemas.items():
        sql = """ CREATE TABLE `{}` (""".format(name)
        for field in stru["fields"]:
            if field["type"] == "string":
                if field["name"] != "problem":
                    sql += "\n`{}` varchar(255) DEFAULT NULL,".format(field["name"])
                elif field["name"] == "problem":
                    sql += "\n`{}` text".format(field["name"])
            elif field["type"] == "integer":
                sql += "\n`{}` int DEFAULT NULL,".format(field["name"])
            elif field["type"] == "number":
                sql += "\n`{}` float DEFAULT 0,".format(field["name"])
            elif field["type"] == "date":
                sql += "\n`{}` varchar(10) DEFAULT NULL,".format(field["name"])
        sql = (
            sql.strip(",")
            + """\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""
        )
        sql += """\nALTER TABLE `{}` ADD PRIMARY KEY (`{}`);""".format(
            name, stru["pkey"]
        )
        schemas[name]["sql"] = sql
    return schemas


def import_data(tablename, df):

    logger.debug('{} rows to write to table "{}"'.format(len(df), tablename))
    rows = df.to_pandas(use_pyarrow_extension_array=True).to_sql(
        name=tablename, con=dbfuncs.alchemy_eng(), if_exists="append", index=False
    )

    logger.debug('{} rows written to table "{}"'.format(rows, tablename))
    for row in dbfuncs.mysql_query_fetchall("SELECT * FROM `{}` LIMIT 1".format(tablename)):
        print(row)


# 'json' to create tables using ./dat/ords/tableschema.json
# If preferred, import 'sql' from ./dat/tableschema_ords_mysql.sql.
# SQL structure gives more fine-grained column sizes, data types may differ though.
# SQL file not guaranteed to always reflect correct schema or to exist in the future.
def create_from_schema(schema="json"):

    try:
        log_tables()
        if schema == "json":
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
                "ALTER TABLE `{}` ADD FULLTEXT KEY (`problem`)".format(table_data)
            )
        elif schema == "sql":
            path = pathfuncs.get_path(
                [cfg.DATA_DIR, "tableschema_ords_mysql.sql"]
            )
            logger.debug('Reading file "{}"'.format(path))
            sql = path.read_text().format(table_cats, table_data)
            dbfuncs.mysql_execute(sql)
        log_tables()
    except Exception as error:
        print("Exception: {}".format(error))


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dbfuncs.dbvars = cfg.get_dbvars()

    table_cats = cfg.get_envvar("ORDS_CATS")
    table_data = cfg.get_envvar("ORDS_DATA")

    drop_table(table_cats)
    drop_table(table_data)
    create_from_schema("json")
    import_data(table_cats, ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS")))
    import_data(table_data, ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")))
