#!/usr/bin/env python3


# Standalone script to dump a JSON dataset for use in data visualisation.

import mysql.connector
import ast
import os
import json
import pandas as pd
from dotenv import load_dotenv


def get_dbvars(con="ORDS_DB_CONN"):

    try:
        dbstr = os.environ.get("ORDS_DB_CONN")
        return dbdict
    except Exception as error:
        print("Exception: {}".format(error))
        return False


def query_fetchall(sql):
    result = False
    try:
        dbvars = ast.literal_eval(os.environ.get("ORDS_DB_CONN"))
        dbh = mysql.connector.connect(
            host=dbvars["host"],
            database=dbvars["database"],
            user=dbvars["user"],
            password=dbvars["pwd"],
        )
        cursor = dbh.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
    except mysql.connector.Error as error:
        print("MySQL exception: {}".format(error))

    finally:
        if dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


if __name__ == "__main__":

    load_dotenv()

    sql = """
        SELECT
        country,
        product_category as product,
        COUNT(*) as records
        FROM `{}`
        WHERE product_category IN ('Kettle', 'Coffee Maker')
        GROUP BY product_category, country
        HAVING records > 50
        ORDER BY country, product_category, records DESC;
        """
    dfsub = pd.DataFrame(query_fetchall(sql.format(os.environ["ORDS_DATA"])))

    dict = (
        dfsub.set_index("country")
        .groupby(level=0)
        .apply(lambda x: x.to_dict("records"))
        .to_dict()
    )

    file = "vis/ords_coffee_v_tea"
    with open(file + ".json", "w") as f:
        json.dump(
            dict,
            f,
            indent=4,
            ensure_ascii=False,
        )
    with open(file + ".json", "r") as f:
        data = f.read()

    with open(file + ".js", "w") as f:
        f.write("data=" + data)
