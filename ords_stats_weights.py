#!/usr/bin/env python3

from funcs import *
import pandas as pd
logger = logfuncs.init_logger(__file__)

tablename = envfuncs.get_var('ORDS_DATA')

# This query exposes some issues with repair data, namely...
# a) categorising products
# b) estimating average weights
# c) values that change over time

# The data file maps categories and average weight estimates between ORDS,
# The Restart Project and UNITAR.
# See dat/README.md for more details.
weights = pd.read_csv(pathfuncs.DATA_DIR +
                      '/ords_category_unu_map.csv')


# fetchfrom = 'df' (DataFrame) or 'db' (Database).
def get_data(fetchfrom='df'):

    if fetchfrom == 'df':
        df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                         keep_default_na=False, na_values="")
        data = df[df.repair_status == 'Fixed'].reindex(
            columns=['product_category'])
        data = data.groupby(
            ['product_category']).size().reset_index(name='records')

    elif fetchfrom == 'db':
        sql = """
        SELECT
        product_category,
        COUNT(*) as records
        FROM `{}`
        WHERE repair_status = 'Fixed'
        GROUP BY product_category
        ORDER BY product_category
        """
        data = pd.DataFrame(dbfuncs.query_fetchall(
            sql.format(tablename)))

    else:
        print("I GIVE UP! GET DATA FROM WHERE EXACTLY?")
        exit()

    return data


# Replace arg with 'db' if fetch from database preferred.
data = get_data('df')

data = data.set_index(
    'product_category').join(weights.set_index('product_category'))
data['trp_2015_total'] = round(data.trp_2015 * data.records, 2)
data['trp_2021_total'] = round(data.trp_2021 * data.records, 2)
# data['unu_1995_total'] = round(data.unu_1995 * data.records, 2)
# data['unu_2000_total'] = round(data.unu_2000 * data.records, 2)
# data['unu_2005_total'] = round(data.unu_2005 * data.records, 2)
# data['unu_2010_total'] = round(data.unu_2010 * data.records, 2)
# data['unu_2011_total'] = round(data.unu_2011 * data.records, 2)
data['unu_2012_total'] = round(data.unu_2012 * data.records, 2)
logger.debug(data)
data.to_csv(pathfuncs.OUT_DIR +
            '/{}_stats_weights.csv'.format(tablename), index=True)
