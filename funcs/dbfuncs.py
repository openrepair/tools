import mysql.connector
import os

# MYSQL database function wrappers.

dbvars = {
    'host': '{ORDS_DB_HOST}'.format(**os.environ),
    'database': '{ORDS_DB_DATABASE}'.format(**os.environ),
    'collation': '{ORDS_DB_COLLATION}'.format(**os.environ),
    'user': '{ORDS_DB_USER}'.format(**os.environ),
    'pwd': '{ORDS_DB_PWD}'.format(**os.environ)
}


def query_fetchall(sql, params=None):
    result = False
    try:
        dbh = mysql_con()
        cursor = dbh.cursor(dictionary=True)
        cursor.execute(sql, params)
        result = cursor.fetchall()
    except mysql.connector.Error as error:
        print("MySQL exception: {}".format(error))
    finally:
        if dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


def execute(sql, params=None):
    result = 0
    try:
        dbh = mysql_con()
        cursor = dbh.cursor()
        cursor.execute(sql, params)
        dbh.commit()
        result = cursor.rowcount
    except mysql.connector.Error as error:
        print("MySQL exception: {}".format(error))
    finally:
        if dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


def executemany(sql, params=None):
    result = 0
    try:
        dbh = mysql_con()
        cursor = dbh.cursor()
        cursor.executemany(sql, params)
        dbh.commit()
        result = cursor.rowcount
    except mysql.connector.Error as error:
        print("MySQL exception: {}".format(error))
    finally:
        if dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


def dump_table_to_csv(table, path):
    import pandas as pd
    sql = """
    SELECT *
    FROM {}
    """.format(table)
    df = pd.DataFrame(query_fetchall(sql))
    path_to_csv = path + '/{}.csv'.format(table)
    df.to_csv(path_to_csv, index=False)
    if os.path.exists(path_to_csv):
        print('Data dumped to {}'.format(path_to_csv))
        return path_to_csv
    else:
        print('Failed to dump data to {}'.format(path_to_csv))
        return False


def mysql_con():
    dbh = False
    try:
        dbh = mysql.connector.connect(
            host=dbvars['host'],
            database=dbvars['database'],
            user=dbvars['user'],
            password=dbvars['pwd'],
            # collation=dbvars['collation'],
            # raw=True
        )
    except mysql.connector.Error as error:
        print("MySQL exception: {}".format(error))

    finally:
        return dbh


def alchemy_con():
    return "mysql+mysqldb://{ORDS_DB_USER}:{ORDS_DB_PWD}@{ORDS_DB_HOST}/{ORDS_DB_DATABASE}".format(**os.environ)


def alchemy_eng():
    from sqlalchemy import create_engine
    con = alchemy_con()
    return create_engine(con)


def table_schemas():
    from funcs import pathfuncs
    import json

    path = pathfuncs.get_path([pathfuncs.ORDS_DIR, 'tableschema.json'])
    if not pathfuncs.check_path(path):
        print('File not found! {}'.format(path))
        return False
    with open(path) as schema_file:
        content = schema_file.read()

    parsed = json.loads(content)
    tables = parsed['resources']
    result = {}
    for table in tables:
        result[pathfuncs.get_filestem(table['path'])] = {
            'pkey': table['schema']['primaryKey'],
            'fields':  table['schema']['fields']}

    return result
