#!/usr/bin/env python3


# Standalone script to dump a JSON dataset for use in data visualisation.

import mysql.connector
import os
import json
import pandas as pd
from dotenv import load_dotenv


def query_fetchall(sql):
    result = False
    try:
        dbh = mysql.connector.connect(
            host=os.environ["ORDS_DB_HOST"],
            database=os.environ["ORDS_DB_DATABASE"],
            user=os.environ["ORDS_DB_USER"],
            password=os.environ["ORDS_DB_PWD"],
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
    with open("vis/ords_coffee_v_tea.json", "w") as f:
        json.dump(
            dfsub.set_index("country").to_dict("records"),
            f,
            indent=4,
            ensure_ascii=False,
        )
