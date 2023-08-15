#!/usr/bin/env python3

from funcs import *
import json
import pandas as pd
logger = logfuncs.init_logger(__file__)

# MYSQL database functions.
# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.

tablename = envfuncs.get_var('ORDS_DATA')


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
    ORDER BY event_date
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(
        sql.format(tablename, '2018', '2022')))
    write_to_files(dfsub, 'events', index=False)


# Products and repairs.
def slice_repairs():

    sql = """
    SELECT
    id,
    product_age,
    year_of_manufacture,
    repair_status,
    repair_barrier_if_end_of_life
    FROM `{}`
    WHERE `product_age` > ''
    ORDER BY product_age
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(sql.format(tablename)))
    # Empty repair_barrier_if_end_of_life values
    dfsub.fillna('', inplace=True)
    write_to_files(dfsub, 'repairs', index=False)


# Year of manufacture.
def slice_year_of_manufacture():
    sql = """
    SELECT
    product_category,
    MIN(year_of_manufacture) AS 'earliest',
    MAX(year_of_manufacture) AS 'latest',
    ROUND(AVG(year_of_manufacture),0) AS 'average'
    FROM `{}`
    WHERE year_of_manufacture > ''
    GROUP BY product_category
    ORDER BY product_category
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(sql.format(tablename)))
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
    WHERE product_age > ''
    GROUP BY product_category
    ORDER BY product_category
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(sql.format(tablename)))
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
    ORDER BY product_category
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(sql.format(tablename)))
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
    IF(INSTR(partner_product_category, '~'),
    TRIM(SUBSTRING_INDEX(partner_product_category, '~', -1)),
    partner_product_category) as item_type
    FROM `{}`
    ) t1
    GROUP BY product_category, item_type
    ORDER BY records DESC
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(sql.format(tablename)))
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
    """
    dfsub = pd.DataFrame(dbfuncs.query_fetchall(sql.format(tablename))).set_index(
        'iso').join(countries.set_index('iso'))
    write_to_files(dfsub, 'countries', index=True)


# Set sample to a fraction to return a subset of results.
# Can be useful for testing, e.g. data visualisation.
def write_to_files(dfsub, suffix, index=False, sample=0):

    if sample:
        dfsub = dfsub.sample(frac=sample, replace=False, random_state=1)

    # json
    if not index:
        dict = dfsub.to_dict('records')
    else:
        dict = dfsub.groupby(level=0).apply(
            lambda x: x.to_dict('records')).to_dict()
    with open(pathfuncs.OUT_DIR +
              '/{}_{}.json'.format(tablename, suffix), 'w') as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)

    # csv
    dfsub.to_csv(pathfuncs.OUT_DIR +
                 '/{}_{}.csv'.format(tablename, suffix), index=index)


slice_events()
slice_repairs()
slice_product_age()
slice_year_of_manufacture()
slice_categories()
slice_item_types()
slice_countries()
