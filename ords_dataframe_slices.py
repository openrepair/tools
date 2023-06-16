#!/usr/bin/env python3

from funcs import *
import json
import pandas as pd
logger = logfuncs.init_logger(__file__)

# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.

# Get the name of the data file from the .env file.
table_data = envfuncs.get_var('ORDS_DATA')

# Read the data file as type string with na values set to empty string.
df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                 keep_default_na=False, na_values="")

# Convert some of the dtypes as appropriate.
df['product_category_id'] = df['product_category_id'].astype('int64')
df['product_age'] = df['product_age'].astype('float64')

# Find a few useful stats.
logger.debug(df.agg({'product_age': ['min', 'max']}))
logger.debug(df.groupby('product_age').agg({'product_age': ['count']}))
logger.debug(df.groupby('year_of_manufacture').agg(
    {'year_of_manufacture': ['count']}))


# Events
# Date range is arbitrary, amend or omit
# Sorted by event_date.
def slice_events():
    df_res = df.reindex(columns=['id', 'data_provider',
                        'event_date', 'group_identifier', 'country'])
    print(df_res.agg({'event_date': ['min', 'max']}))
    print(df_res.groupby('event_date').agg({'event_date': ['count']}))
    df_res.sort_values(by='event_date', ascending=True,
                       inplace=True, ignore_index=True)
    df_res = df_res.loc[(df_res['event_date'] > '2018') &
                        (df_res['event_date'] < '2022')]
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_events.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_events.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


# Products and repairs.
# NaN dropped for product_age
# Sorted by product_age.
def slice_repairs():
    df_res = df.reindex(columns=['id', 'product_age', 'year_of_manufacture',
                        'repair_status', 'repair_barrier_if_end_of_life'])
    df_res.dropna(axis='rows', subset=[
        'product_age'], inplace=True, ignore_index=True)
    df_res.sort_values(by=['product_age'], ascending=True,
                       inplace=True, ignore_index=True)
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_repairs.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_repairs.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


# Product age.
def slice_product_age():
    df_res = df.reindex(columns=['product_category', 'product_age'])
    df_res.dropna(axis='rows', subset=[
        'product_age'], inplace=True, ignore_index=True)
    df_res = df_res.groupby('product_category').agg(
        {'product_age': ['min', 'max', 'mean']})
    df_res.columns = ['earliest', 'latest', 'average']
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_product_age.csv'.format(table_data))
    with open(pathfuncs.OUT_DIR +
              '/{}_product_age.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


# Year of manufacture.
def slice_year_of_manufacture():
    df_res = df.reindex(columns=['product_category', 'year_of_manufacture'])
    df_res.dropna(axis='rows', subset=[
        'year_of_manufacture'], inplace=True, ignore_index=True)
    df_res['year_of_manufacture'] = df_res['year_of_manufacture'].astype(
        'int64')
    df_res = df_res.groupby('product_category').agg(
        {'year_of_manufacture': ['min', 'max', 'mean']})
    df_res.columns = ['newest', 'oldest', 'average']
    df_res['average'] = df_res['average'].astype(int)
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_year_of_manufacture.csv'.format(table_data))
    with open(pathfuncs.OUT_DIR +
              '/{}_year_of_manufacture.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


# Product categories.
# Sorted by product_category.
def slice_categories():
    df_res = df.reindex(
        columns=['id', 'partner_product_category', 'product_category', 'repair_status'])
    df_res.sort_values(by=['product_category'],
                       ascending=True, inplace=True, ignore_index=True)
    df_res.to_csv(pathfuncs.OUT_DIR +
                  '/{}_categories.csv'.format(table_data), index=False)
    with open(pathfuncs.OUT_DIR +
              '/{}_categories.json'.format(table_data), 'w') as f:
        json.dump(df_res.to_dict('records'), f, indent=4, ensure_ascii=False)


# Item types.
# Split the partner_product_category string.
def slice_item_types():
    df_res = df['partner_product_category'].reset_index(drop=True).squeeze()
    np_res = df_res.str.split('~').str.get(1).str.strip().dropna().unique()
    df_res = pd.DataFrame(np_res, columns=['item_type'])
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
