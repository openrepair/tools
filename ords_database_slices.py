#!/usr/bin/env python3

from funcs import *
import json
import pandas as pd
logger = logfuncs.init_logger(__file__)

# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.

table_data = envfuncs.get_var('ORDS_DATA')


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
    df_res = pd.DataFrame(dbfuncs.query_fetchall(
        sql.format(table_data, '2018', '2022')))
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_events.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_events.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


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
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql.format(table_data)))
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_repairs.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_repairs.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


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
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql.format(table_data)))
    df_res['average'] = df_res['average'].astype(int)
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_year_of_manufacture.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_year_of_manufacture.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


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
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql.format(table_data)))
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_product_age.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_product_age.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


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
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql.format(table_data)))
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_categories.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_categories.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


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
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql.format(table_data)))
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_item_types.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_item_types.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


slice_events()
slice_repairs()
slice_product_age()
slice_year_of_manufacture()
slice_categories()
slice_item_types()
