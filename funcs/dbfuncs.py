import mysql.connector
import os


dbvars = {
    'host': '{ORDS_DB_HOST}'.format(**os.environ),
    'database': '{ORDS_DB_DATABASE}'.format(**os.environ),
    'collation': '{ORDS_DB_COLLATION}'.format(**os.environ),
    'user': '{ORDS_DB_USER}'.format(**os.environ),
    'pwd': '{ORDS_DB_PWD}'.format(**os.environ)
}


def dbtest():
    print("This is the ORDS dbfuncs module")
    return dbvars

# https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html


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


def alchemy_con():
    return "mysql+mysqldb://{ORDS_DB_USER}:{ORDS_DB_PWD}@{ORDS_DB_HOST}/{ORDS_DB_DATABASE}".format(**os.environ)


def alchemy_eng():
    from sqlalchemy import create_engine
    con = alchemy_con()
    return create_engine(con)


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


def create_ords_tables(sql):
    result = False
    try:
        dbh = mysql_con()
        cursor = dbh.cursor(dictionary=True)
        result = cursor.execute(sql)
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
    """
    df = pd.DataFrame(query_fetchall(sql.format(table)))
    path_to_csv = path + '/{}.csv'.format(table)
    df.to_csv(path_to_csv, index=False)
    if os.path.exists(path_to_csv):
        print('Data dumped to {}'.format(path_to_csv))
        return path_to_csv
    else:
        print('Failed to dump data to {}'.format(path_to_csv))
        return False
