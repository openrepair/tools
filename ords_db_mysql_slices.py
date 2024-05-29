#!/usr/bin/env python3

import polars as pl
from funcs import *

# MYSQL database functions.
# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.


# Events - date range is arbitrary, amend or omit.
def slice_events():

    sql = f"""
    SELECT
    id,
    data_provider,
    event_date,
    group_identifier,
    country
    FROM `{tablename}`
    WHERE event_date BETWEEN '2018' AND '2022'
    ORDER BY event_date, id
    """
    dfsub = pl.DataFrame(
        dbfuncs.mysql_query_fetchall(sql)
    )
    write_to_files(dfsub, "events")


# Products and repairs.
def slice_repairs():

    sql = f"""
    SELECT
    id,
    product_age,
    year_of_manufacture,
    repair_status,
    repair_barrier_if_end_of_life
    FROM `{tablename}`
    WHERE `product_age` > 0
    ORDER BY product_age, id
    """
    dfsub = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql)).fill_null("")
    write_to_files(dfsub, "repairs")


# Year of manufacture.
def slice_year_of_manufacture():
    sql = f"""
    SELECT
    product_category,
    MIN(year_of_manufacture) AS 'earliest',
    MAX(year_of_manufacture) AS 'latest',
    ROUND(AVG(year_of_manufacture),0) AS 'average'
    FROM `{tablename}`
    WHERE year_of_manufacture > ''
    GROUP BY product_category
    ORDER BY product_category
    """
    dfsub = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql))
    write_to_files(dfsub, "year_of_manufacture", sample=0)


# Product age.
# 0 usually means < 1 year old.
# Value can be float, e.g. 1.5 = 1 year and 6 months.
def slice_product_age():
    sql = f"""
    SELECT
    product_category,
    MIN(product_age) AS 'newest',
    MAX(product_age) AS 'oldest',
    ROUND(AVG(product_age),1) AS 'average'
    FROM `{tablename}`
    WHERE product_age > 0
    GROUP BY product_category
    ORDER BY product_category
    """
    dfsub = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql))
    write_to_files(dfsub, "product_age", sample=0)


# Product categories.
def slice_categories():

    sql = f"""
    SELECT
    id,
    partner_product_category,
    product_category,
    repair_status
    FROM `{tablename}`
    ORDER BY product_category, id
    """
    dfsub = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql))
    write_to_files(dfsub, "categories")


# Item types.
def slice_item_types():
    sql = f"""
    SELECT
    t1.product_category,
    t1.item_type,
    COUNT(*) as records
    FROM (
    SELECT
    product_category,
    TRIM(IF(INSTR(partner_product_category, '~'),
    SUBSTRING_INDEX(partner_product_category, '~', -1),
    partner_product_category)) as item_type
    FROM `{tablename}`
    ) t1
    GROUP BY product_category, item_type
    ORDER BY product_category, records DESC
    """
    dfsub = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql))
    write_to_files(dfsub, "item_types")


# Countries and groups.
def slice_countries():

    countries = pl.read_csv(cfg.DATA_DIR + "/iso_country_codes.csv")

    sql = f"""
    SELECT
    country as iso,
    group_identifier as `group`,
    COUNT(*) as records
    FROM `{tablename}`
    GROUP BY country, group_identifier
    ORDER BY country, group_identifier
    """
    dfsub = pl.DataFrame(dbfuncs.mysql_query_fetchall(sql))
    dfsub = dfsub.join(countries, on="iso", how="left")
    write_to_files(dfsub, "countries")


# Set sample to a fraction to return a subset of results.
# Can be useful for testing, e.g. data visualisation.
def write_to_files(dfsub, suffix, sample=0):

    if sample:
        dfsub = dfsub.sample(fraction=sample)

    path = f"{cfg.OUT_DIR}/{tablename}_{suffix}.csv"
    dfsub.write_csv(path)
    print(path)


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dbfuncs.dbvars = cfg.get_dbvars()

    tablename = cfg.get_envvar("ORDS_DATA")

    slice_events()
    slice_repairs()
    slice_year_of_manufacture()
    slice_product_age()
    slice_categories()
    slice_item_types()
    slice_countries()
