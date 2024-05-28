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


def backup_only():
    try:
        sql = """
        SELECT *
        FROM ords_problem_translations
        """
        df = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql))
        path_to_csv = cfg.OUT_DIR + "/ords_problem_translations_{}.csv".format(
            datefuncs.format_curr_datetime()
        )
        pathfuncs.rm_file(path_to_csv)
        df.to_csv(path_to_csv, index=False)
        if pathfuncs.check_path(path_to_csv):
            print("Backup written to {}".format(path_to_csv))
            return path_to_csv
        else:
            print("Failed to write data to {}".format(path_to_csv))
    except Exception as error:
        print("Exception: {}".format(error))
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
    dbfuncs.mysql_execute(sql)

    logger.debug(f"{len(df)} rows to write to table {tablename}")
    rows = df.to_pandas(use_pyarrow_extension_array=True).to_sql(
        name=tablename, con=dbfuncs.alchemy_eng(), if_exists="append", index=False
    )
    logger.debug(f"{rows} written to table {tablename}")


def backup_and_replace_file():
    path_to_csv_new = backup_only()
    path_to_csv_old = f"{cfg.DATA_DIR}/ords_problem_translations.csv"
    pathfuncs.copy_file(path_to_csv_new, path_to_csv_old)


# Select function to run.
def exec_opt(options):
    while True:
        for i, desc in options.items():
            print(f"{i} : {desc}")
        choice = input("Type a number: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice")
        else:
            if choice >= len(options):
                print("Out of range")
            else:
                f = options[choice]
                print(f)
                eval(f)


def get_options():
    return {
        0: "exit()",
        1: "backup_only()",
        2: "backup_and_replace_file()",
        3: "setup_database()",
    }


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dbfuncs.dbvars = cfg.get_dbvars()

    exec_opt(get_options())
