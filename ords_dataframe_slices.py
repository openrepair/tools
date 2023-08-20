#!/usr/bin/env python3

from funcs import *
import json
import pandas as pd
logger = logfuncs.init_logger(__file__)

# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.

# Get the name of the data file from the .env file.
tablename = envfuncs.get_var('ORDS_DATA')

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
    dfsub = df.reindex(columns=['id', 'data_provider',
                                'event_date', 'group_identifier', 'country'])
    dfsub.sort_values(by='event_date', ascending=True,
                      inplace=True, ignore_index=True)
    dfsub = dfsub.loc[(dfsub['event_date'] > '2018') &
                      (dfsub['event_date'] < '2022')]
    write_to_files(dfsub, 'events', index=False)


# Products and repairs.
# NaN dropped for product_age
# Sorted by product_age.
def slice_repairs():
    dfsub = df.reindex(columns=['id', 'product_age', 'year_of_manufacture',
                                'repair_status', 'repair_barrier_if_end_of_life'])
    dfsub.dropna(axis='rows', subset=[
        'product_age'], inplace=True, ignore_index=True)
    # Empty repair_barrier_if_end_of_life values
    dfsub.fillna('', inplace=True)
    dfsub.sort_values(by=['product_age'], ascending=True,
                      inplace=True, ignore_index=True)
    write_to_files(dfsub, 'repairs', index=False)


# Product age.
def slice_product_age():
    dfsub = df.reindex(columns=['product_category', 'product_age'])
    dfsub.dropna(axis='rows', subset=[
        'product_age'], inplace=True, ignore_index=True)
    dfsub = dfsub.groupby('product_category').agg(
        {'product_age': ['min', 'max', 'mean']})
    dfsub.columns = ['earliest', 'latest', 'average']
    write_to_files(dfsub, 'product_age', index=True)


# Year of manufacture.
def slice_year_of_manufacture():
    dfsub = df.reindex(columns=['product_category', 'year_of_manufacture'])
    dfsub.dropna(axis='rows', subset=[
        'year_of_manufacture'], inplace=True, ignore_index=True)
    dfsub['year_of_manufacture'] = dfsub['year_of_manufacture'].astype(
        'int64')
    dfsub = dfsub.groupby('product_category').agg(
        {'year_of_manufacture': ['min', 'max', 'mean']})
    dfsub.columns = ['newest', 'oldest', 'average']
    dfsub['average'] = dfsub['average'].astype(int)
    write_to_files(dfsub, 'year_of_manufacture', index=True)


# Product categories.
# Sorted by product_category.
def slice_categories():
    dfsub = df.reindex(
        columns=['id', 'partner_product_category', 'product_category', 'repair_status'])
    dfsub.sort_values(by=['product_category'],
                      ascending=True, inplace=True, ignore_index=True)
    write_to_files(dfsub, 'categories', index=False)


# Item types.
# Split the partner_product_category string.
def slice_item_types():
    dfsub = df['partner_product_category'].reset_index(drop=True).squeeze()
    np_res = dfsub.str.split('~').str.get(1).str.strip().dropna().unique()
    dfsub = pd.DataFrame(np_res, columns=['item_type'])
    write_to_files(dfsub, 'item_types', index=False)


# Countries and groups.
def slice_countries():

    countries = pd.read_csv(pathfuncs.DATA_DIR +
                            '/iso_country_codes.csv')

    dfsub = df.reindex(
        columns=['country', 'group_identifier']).rename(columns={'country': 'iso',
                                                                 'group_identifier': 'group'})
    dfsub = dfsub.groupby(
        ['iso', 'group']).size().reset_index(name='records')

    dfsub = pd.merge(dfsub.reset_index(), countries,  how='inner',
                         left_on=['iso'],
                         right_on=['iso']).set_index('index')

    write_to_files(dfsub, 'countries', index=False)


# Set sample to a fraction to return a subset of results.
# Can be useful for testing, e.g. data visualisation.
def write_to_files(df, suffix, index=False, sample=0):

    if sample:
        df = df.sample(frac=sample, replace=False, random_state=1)

    path = '{}/{}_{}'.format(pathfuncs.OUT_DIR, tablename, suffix)
    results = miscfuncs.write_data_to_files(df, path, index)
    for result in results:
        print(result)


slice_events()
slice_repairs()
slice_product_age()
slice_year_of_manufacture()
slice_categories()
slice_item_types()
slice_countries()
