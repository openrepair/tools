#!/usr/bin/env python3

from funcs import *
import pandas as pd

logger = logfuncs.init_logger(__file__)

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


def dbbackup():
    sql = """
    SELECT *
    FROM ords_problem_translations
    """
    df = pd.DataFrame(dbfuncs.query_fetchall(sql))
    path_to_csv = pathfuncs.DATA_DIR + \
        '/backup_{}.csv'.format(datefuncs.format_curr_datetime())
    pathfuncs.rm_file(path_to_csv)
    df.to_csv(path_to_csv, index=False)
    if pathfuncs.check_path(path_to_csv):
        print('Backup written to {}'.format(path_to_csv))
        return path_to_csv
    else:
        print('Failed to write data to {}'.format(path_to_csv))
        return False


def dbsetup(path_to_csv=''):

    # Check for path_to_csv.
    if path_to_csv == '':
        path_to_csv = pathfuncs.DATA_DIR + '/ords_problem_translations.csv'

    if not pathfuncs.check_path(path_to_csv):
        print('ERROR: {} NOT FOUND!'.format(path_to_csv))
        return False

    logger.debug('Reading data from file {}'.format(path_to_csv))
    df = pd.read_csv(path_to_csv)

    # Get translations table schema.
    path_to_sql = pathfuncs.get_path(
        [pathfuncs.DATA_DIR + '/tableschema_translations_mysql.sql'])
    print(path_to_sql)
    logger.debug('Reading sql from file {}'.format(path_to_sql))
    # Create table.
    sql = path_to_sql.read_text().format(tablename='ords_problem_translations')
    dbfuncs.execute(sql)

    # Import existing translations.
    rows = df.to_sql(name='ords_problem_translations', con=dbfuncs.alchemy_eng(),
                     if_exists='append', index=False)
    logger.debug('{} written to table "{}"'.format(
        rows, 'ords_problem_translations'))


def replace_csv_file(path_to_csv_new):

    path_to_csv_old = pathfuncs.DATA_DIR + \
        '/ords_problem_translations.csv'
    pathfuncs.rm_file(path_to_csv_old)
    pathfuncs.copy_file(path_to_csv_new, path_to_csv_old)


# START

path_to_csv = dbbackup()

# Replace the csv file with the table dump file?
replace = False
if replace:
    replace_csv_file(path_to_csv)

# Drop and recreate table, import data from csv file.
clean = False
if clean:
    dbsetup()
