#!/usr/bin/env python3

"""
Series of scripts for translating ORDS `problem` text.

https://github.com/DeepLcom/deepl-python

Step 1: ords_deepl_1setup.py
    Table created, MySQL database required.
Step 2: ords_deepl_2fetch.py
    Compiles workload, translates, DeepL API key required.
Step 3: ords_deepl_3check.py
    Inspect data integrity.
Step 4: ords_deepl_4backfill.py
    Translate missing values for given languages.
"""

import polars as pl
from funcs import *


def test_binary_collation():

    schema = {
        "id_ords": pl.String,
        "problem": pl.String,
    }
    # schema = None
    try:
        # res = dbfuncs.mysql_query_fetchall("SELECT id, CAST(problem AS CHAR) FROM `OpenRepairData_v0.3_aggregate_202407`")
        res = dbfuncs.mysql_query_fetchall(
            "SELECT id_ords, CAST(problem AS CHAR) as problem FROM ords_problem_translations"
        )
        df = pl.DataFrame(res)  # , schema=schema, infer_schema_length=1000)
        logger.debug(df.schema)
        path_to_csv = f"{cfg.OUT_DIR}/test2_ords_problem_translations_{datefuncs.format_curr_datetime()}.csv"
        pathfuncs.rm_file(path_to_csv)
        df.write_csv(path_to_csv)
        if pathfuncs.check_path(path_to_csv):
            print(f"Backup written to {path_to_csv}")
            return path_to_csv
        else:
            print(f"Failed to write data to {path_to_csv}")
    except Exception as error:
        print(f"Exception: {error}")
        return False


def backup_only():

    sql = "SELECT * FROM ords_problem_translations"
    try:
        res = dbfuncs.mysql_query_fetchall(sql)
        df = pl.DataFrame(res)
        logger.debug(df.schema)
        path_to_csv = f"{cfg.OUT_DIR}/ords_problem_translations_{datefuncs.format_curr_datetime()}.csv"
        pathfuncs.rm_file(path_to_csv)
        df.write_csv(path_to_csv)
        if pathfuncs.check_path(path_to_csv):
            print(f"Backup written to {path_to_csv}")
            return path_to_csv
        else:
            print(f"Failed to write data to {path_to_csv}")
    except Exception as error:
        print(f"Exception: {error}")
        return False


def setup_database():

    tablename = "ords_problem_translations"
    path_to_csv = f"{cfg.DATA_DIR}/{tablename}.csv"

    if not pathfuncs.check_path(path_to_csv):
        print(f"ERROR: FILE NOT FOUND! {path_to_csv}")
        return False

    logger.debug(f"Reading data from file {path_to_csv}")
    df = pl.read_csv(path_to_csv)

    # Get translations table schema.
    path_to_sql = pathfuncs.get_path(
        [f"{cfg.DATA_DIR}/tableschema_translations_mysql.sql"]
    )
    print(path_to_sql)
    logger.debug(f"Reading sql from file {path_to_sql}")
    # Create table.
    sql = path_to_sql.read_text().format(tablename="tablename")
    dbfuncs.mysql_execute_multi(sql)

    logger.debug(f"{len(df)} rows to write to table {tablename}")
    rows = df.to_pandas(use_pyarrow_extension_array=True).to_sql(
        name=tablename, con=dbfuncs.alchemy_eng(), if_exists="append", index=False
    )
    logger.debug(f"{rows} written to table {tablename}")


def backup_and_replace_file():

    path_to_csv_new = backup_only()
    path_to_csv_old = f"{cfg.DATA_DIR}/ords_problem_translations.csv"
    pathfuncs.copy_file(path_to_csv_new, path_to_csv_old)


# Remove redundant translation records.
# Put sql files in dat/tmp
def cleanup_table():
    """SELECT
    t.id_ords, o.problem as problem_ords, t.problem as problem_trans
    FROM `OpenRepairData_v0.3_aggregate_202407` o
    JOIN  ords_problem_translations t ON o.id = t.id_ords
    WHERE LENGTH(o.problem) < 6;
    """
    logger.debug("*** cleanup_table() ***")

    sqlcount = "SELECT COUNT(*) as recs FROM ords_problem_translations"
    rows = dbfuncs.mysql_query_fetchall(sqlcount)
    rows_bef = rows[0]["recs"]

    sqlfiles = pathfuncs.file_list(f"{cfg.DATA_DIR}tmp")

    for sqlfile in sqlfiles:
        path = f"{sqlfile[0]}/{sqlfile[1]}"
        logger.debug(path)
        with open(path) as f:
            sql = f.read()
        rows = dbfuncs.mysql_execute_multi(sql)
        if rows == None:
            print(f"ERROR: {path} FAILED")
            exit()
        logger.debug(f"{rows} rows updated")

    rows = dbfuncs.mysql_query_fetchall(sqlcount)
    logger.debug(rows)
    rows_aft = rows[0]["recs"]
    rows_diff = rows_bef - rows_aft
    logger.debug(f"Rows deleted: {rows_bef}-{rows_aft}={rows_diff}")


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dbfuncs.dbvars = cfg.get_dbvars()

    while True:
        eval(
            miscfuncs.exec_opt(
                [
                    "backup_only()",
                    "backup_and_replace_file()",
                    "setup_database()",
                    "cleanup_table()",
                ]
            )
        )
