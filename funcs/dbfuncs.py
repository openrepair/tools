import mysql.connector
import sqlite3
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

dbvars = {
    "host": "{ORDS_DB_HOST}".format(**os.environ),
    "database": "{ORDS_DB_DATABASE}".format(**os.environ),
    "collation": "{ORDS_DB_COLLATION}".format(**os.environ),
    "user": "{ORDS_DB_USER}".format(**os.environ),
    "pwd": "{ORDS_DB_PWD}".format(**os.environ),
}


def mysql_query_fetchall(sql, params=None):
    result = False
    try:
        dbh = mysql_connection()
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


def mysql_execute(sql, params=None):
    result = 0
    try:
        dbh = mysql_connection()
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


def mysql_executemany(sql, params=None):
    result = 0
    try:
        dbh = mysql_connection()
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


def mysql_show_create_table(name):
    result = False
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor(dictionary=True)
        sql = "SHOW CREATE TABLE `{}`".format(name)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            result = row["Create Table"]
    except Exception as error:
        pass
        # result = "Table not found: {}".format(name)
    finally:
        if dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


# def mysql_dump_table_to_csv(table, path):

#     sql = """
#     SELECT *
#     FROM {}
#     """.format(table)
#     df = pd.DataFrame(mysql_query_fetchall(sql))
#     path_to_csv = path + '/{}.csv'.format(table)
#     df.to_csv(path_to_csv, index=False)
#     if os.path.exists(path_to_csv):
#         print('Data dumped to {}'.format(path_to_csv))
#         return path_to_csv
#     else:
#         print('Failed to dump data to {}'.format(path_to_csv))
#         return False


def mysql_connection():
    dbh = False
    try:
        dbh = mysql.connector.connect(
            host=dbvars["host"],
            database=dbvars["database"],
            user=dbvars["user"],
            password=dbvars["pwd"],
            # collation=dbvars['collation'],
            # raw=True
        )
    except mysql.connector.Error as error:
        print("MySQL exception: {}".format(error))

    finally:
        return dbh


def alchemy_constr():
    return "mysql+mysqldb://{ORDS_DB_USER}:{ORDS_DB_PWD}@{ORDS_DB_HOST}/{ORDS_DB_DATABASE}".format(
        **os.environ
    )


def alchemy_eng():
    con = alchemy_constr()
    return create_engine(con)


def sqlite_dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def sqlite_connection():
    con = False
    try:
        con = sqlite3.connect(dbvars["database"])
        con.row_factory = sqlite_dict_factory
    except sqlite3.Error as error:
        print("Exception: {}".format(error))
    finally:
        return con


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
