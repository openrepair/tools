#!/usr/bin/env python3

from funcs import *
import re
import pandas as pd
logger = logfuncs.init_logger(__file__)

# Compile a table of common item types using multi-lingual regular expressions.

# Create a structure to hold results.
mapcols = ['product_category', 'term', 'records', 'matches']
results = pd.DataFrame(columns=mapcols)

rexes = pd.read_csv(pathfuncs.DATA_DIR + '/product_category_regexes.csv')
# There should be no empty regex strings but just in case.
rexes.dropna(inplace=True)

# Pre-compile the regexes
for n in range(0, len(rexes)):
    rexes.loc[n, 'obj'] = re.compile(rexes.iloc[n]['regex'], re.I)

# Changes to the ORDS categories will require updates to the regexes.
categories = pd.read_csv(pathfuncs.ORDS_DIR +
                         '/{}.csv'.format(envfuncs.get_var('ORDS_CATS')))

tablename = envfuncs.get_var('ORDS_DATA')


def get_data_from_db(category_id):
    sql = """
    SELECT
    t1.item_type,
    COUNT(*) as records
    FROM (
    SELECT
    IF(INSTR(partner_product_category, '~'),
    TRIM(SUBSTRING_INDEX(partner_product_category, '~', -1)),
    partner_product_category) as item_type
    FROM `{}`
    WHERE product_category_id = {}
    ) t1
    GROUP BY item_type
    ORDER BY records DESC
    """
    df = pd.DataFrame(dbfuncs.query_fetchall(
        sql.format(tablename, category_id)))
    logger.debug(df.columns)
    return df


# Fetch data from csv into frame.
# ToDo: find why result differs slightly from get_data_from_db()
def get_data_from_df(category_id):
    df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                    keep_default_na=False, na_values="")
    df = df.loc[df['product_category_id'].astype('int64') == category_id]
    df.partner_product_category = df.partner_product_category.str.split('~').str.get(1).str.strip()
    df.rename(columns={'partner_product_category': 'item_type'}, inplace=True)
    logger.debug(df)
    df = df.groupby(
        ['item_type']).size().reset_index(name='records')
    logger.debug(df.columns)
    df.sort_values(by=['records'],
                   ascending=False, inplace=True, ignore_index=True)
    return df


# Fetch the regex for the given category.
def get_regex(category):
    regex = rexes.loc[(rexes.product_category == category)]
    if (not regex.empty and regex.product_category.count() == 1):
        return regex.obj.iloc[0]
    return False


# Return regex matching information for a given term.
def get_matches(category, row, rx):
    if (rx):
        matches = rx.search(row['item_type'])
        if matches:
            return [category, row['item_type'], row['records'], matches.group()]
    return False


# Main loop.
for n in range(0, len(categories)):
    category = categories.iloc[n].product_category
    logger.debug('*** {} ***'.format(category))
    print('*** {} ***'.format(category))
    data = get_data_from_db(categories.iloc[n].product_category_id)
    rx = get_regex(category)
    for i in range(0, len(data)):
        logger.debug('{}'.format(data.loc[i]))
        matches = get_matches(category, data.loc[i], rx)
        if matches:
            results.loc[len(results)] = matches

# Write results to csv format file.
results.to_csv(pathfuncs.OUT_DIR +
               '/ords_regex_category_item_types.csv', index=False)
