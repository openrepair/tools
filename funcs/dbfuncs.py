import mysql.connector
import sqlite3
from sqlalchemy import create_engine

dbvars = None


def mysql_query_fetchall(sql, params=None):
    result = False
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor(dictionary=True)
        cursor.execute(sql, params)
        cursor._check_executed()
        result = cursor.fetchall()
    except mysql.connector.Error as error:
        print(f"MYSQL EXCEPTION: {error}")
    finally:
        if (dbh != None) & dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


def mysql_execute_multi(sql):
    result = []
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor()
        for q in cursor.execute(sql, multi=True):
            result.append([q.statement, q.rowcount])
    except Exception as error:
        print(f"MYSQL EXCEPTION: {error}")
    finally:
        if (dbh != None) & dbh.is_connected():
            dbh.commit()
            cursor.close()
            dbh.close()
        return result


def mysql_execute(sql, params=None, rowcount=True):
    result = None
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor()
        cursor.execute(sql, params)
        cursor._check_executed()
        dbh.commit()
        if rowcount:
            result = cursor.rowcount
        else:
            result = True
    except mysql.connector.Error as error:
        print(f"MYSQL EXCEPTION: {error}")
    finally:
        if (dbh != None) & dbh.is_connected():
            dbh.commit()
            cursor.close()
            dbh.close()
        return result


def mysql_executemany(sql, params=None, rowcount=True):
    result = None
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor()
        cursor.executemany(sql, params)
        cursor._check_executed()
        dbh.commit()
        if rowcount:
            result = cursor.rowcount
        else:
            result = True
    except mysql.connector.Error as error:
        print(f"MYSQL EXCEPTION: {error}")
        result = False
    finally:
        if (dbh != None) & dbh.is_connected():
            dbh.commit()
            cursor.close()
            dbh.close()
        return result


def mysql_create_table(sql):
    result = None
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor()
        cursor.execute(sql)
        result = True
    except mysql.connector.Error as error:
        print(f"MYSQL EXCEPTION: {error}")
        result = False
    finally:
        if (dbh != None) & dbh.is_connected():
            dbh.commit()
            cursor.close()
            dbh.close()
        return result


def mysql_show_create_table(name):
    result = None
    try:
        dbh = mysql_connection()
        cursor = dbh.cursor(dictionary=True)
        sql = f"SHOW CREATE TABLE `{name}`"
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            result = row["Create Table"]
    except Exception as error:
        print(f"MYSQL EXCEPTION: {error}")
        result = False
    finally:
        if (dbh != None) & dbh.is_connected():
            dbh.commit()
            cursor.close()
            dbh.close()
        return result


def mysql_connection():
    try:
        return mysql.connector.connect(
            host=dbvars["host"],
            database=dbvars["database"],
            user=dbvars["user"],
            password=dbvars["pwd"],
        )
    except mysql.connector.Error as error:
        print(f"MYSQL EXCEPTION: {error}")
        return False


def alchemy_constr():
    return f'mysql+mysqldb://{dbvars["user"]}:{dbvars["pwd"]}@{dbvars["host"]}/{dbvars["database"]}'


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
        print(f"Exception: {error}")
    finally:
        return con


def dump_table_to_csv(table, path):
    import os
    import pandas as pd

    sql = """
    SELECT *
    FROM {}
    """.format(
        table
    )
    df = pd.DataFrame(mysql_query_fetchall(sql))
    path_to_csv = path + "/{}.csv".format(table)
    df.to_csv(path_to_csv, index=False)
    if os.path.exists(path_to_csv):
        print("Data dumped to {}".format(path_to_csv))
        return path_to_csv
    else:
        print("Failed to dump data to {}".format(path_to_csv))
        return False
