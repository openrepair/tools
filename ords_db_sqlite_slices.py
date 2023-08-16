#!/usr/bin/env python3

from funcs import *
import pandas as pd
import json

logger = logfuncs.init_logger(__file__)

# SQLite database functions.
# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.

tablename = envfuncs.get_var('ORDS_DATA')

con = dbfuncs.sqlite_connect()


# Events - date range is arbitrary, amend or omit.
def slice_events():

    sql = """
    SELECT
    id,
    data_provider,
    event_date,
    group_identifier,
    country
    FROM `{}`
    WHERE event_date BETWEEN '{}' AND '{}'
    ORDER BY event_date, id
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename, '2018', '2022')))
    write_to_files(dfsub, 'events', index=False)


# Products and repairs.
def slice_repairs():

    sql = """
    SELECT
    id,
    product_age,
    CAST("year_of_manufacture" AS int) AS year_of_manufacture,
    repair_status,
    repair_barrier_if_end_of_life
    FROM `{}`
    WHERE `product_age` > 0
    ORDER BY product_age, id
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename)))
    # Empty repair_barrier_if_end_of_life values
    dfsub.fillna('', inplace=True)
    write_to_files(dfsub, 'repairs', index=False)


# Year of manufacture.
def slice_year_of_manufacture():
    sql = """
    SELECT
    product_category,
    CAST(MIN(year_of_manufacture) AS int) AS 'earliest',
    CAST(MAX(year_of_manufacture) AS int) AS 'latest',
    CAST(ROUND(AVG(year_of_manufacture),0) AS int) AS 'average'
    FROM `{}`
    WHERE year_of_manufacture > ''
    GROUP BY product_category
    ORDER BY product_category
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename)))
    dfsub['average'] = dfsub['average'].astype(int)
    write_to_files(dfsub, 'year_of_manufacture', index=False, sample=0)


# Product age.
# 0 usually means < 1 year old.
# Value can be float, e.g. 1.5 = 1 year and 6 months.
def slice_product_age():
    sql = """
    SELECT
    product_category,
    MIN(product_age) AS 'newest',
    MAX(product_age) AS 'oldest',
    ROUND(AVG(product_age),1) AS 'average'
    FROM `{}`
    WHERE product_age > 0
    GROUP BY product_category
    ORDER BY product_category
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename)))
    write_to_files(dfsub, 'product_age', index=False, sample=0)


# Product categories.
def slice_categories():

    sql = """
    SELECT
    id,
    partner_product_category,
    product_category,
    repair_status
    FROM `{}`
    ORDER BY product_category, id
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename)))
    write_to_files(dfsub, 'categories', index=False)


# Item types.
def slice_item_types():
    sql = """
    SELECT
    t1.product_category,
    t1.item_type,
    COUNT(*) as records
    FROM (
    SELECT
    product_category,
    TRIM(SUBSTR(partner_product_category,
    INSTR(partner_product_category, '~')+IIF(INSTR(partner_product_category, '~')=0,0,2))
    ) as item_type
    FROM `{}`
    ) t1
    GROUP BY product_category, item_type
    ORDER BY records DESC
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename)))
    write_to_files(dfsub, 'item_types', index=False)


# Countries and groups.
def slice_countries():

    countries = pd.read_csv(pathfuncs.DATA_DIR +
                            '/iso_country_codes.csv')

    sql = """
    SELECT
    country as iso,
    group_identifier as `group`,
    COUNT(*) as records
    FROM `{}`
    GROUP BY country, group_identifier
    ORDER BY country, group_identifier
    """
    dfsub = pd.DataFrame(con.execute(sql.format(tablename))).set_index(
        'iso').join(countries.set_index('iso'))
    write_to_files(dfsub, 'countries', index=True)


# Set sample to a fraction to return a subset of results.
# Can be useful for testing, e.g. data visualisation.
def write_to_files(dfsub, suffix, index=False, sample=0):

    path = '{}/{}_{}'.format(pathfuncs.OUT_DIR, tablename, suffix)
    results = miscfuncs.write_data_to_files(dfsub, path, index)
    for result in results:
        print(result)


slice_events()
slice_repairs()
slice_year_of_manufacture()
slice_product_age()
slice_categories()
slice_item_types()
slice_countries()
