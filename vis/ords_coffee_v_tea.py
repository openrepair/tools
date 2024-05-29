#!/usr/bin/env python3


# Standalone script to dump a JSON dataset for use in data visualisation.

import mysql.connector
import ast
import os
import json
import pandas as pd
from dotenv import load_dotenv


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
        print(f"MySQL Exception: {error}")

    finally:
        if dbh.is_connected():
            cursor.close()
            dbh.close()
        return result


if __name__ == "__main__":

    load_dotenv()

    sql = f"""SELECT
country,
product_category as product,
COUNT(*) as records
FROM `{os.environ['ORDS_DATA']}`
WHERE country IN ((
    SELECT
    country
    FROM `{os.environ['ORDS_DATA']}`
    WHERE product_category IN ('Kettle', 'Coffee Maker')
    GROUP BY country
    HAVING COUNT(*) > 100
))
AND product_category IN ('Kettle', 'Coffee Maker')
GROUP BY country, product
ORDER BY country, product
    """
    dfsub = pd.DataFrame(query_fetchall(sql))

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
