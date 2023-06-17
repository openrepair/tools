#!/usr/bin/env python3

from funcs import *
import pandas as pd
logger = logfuncs.init_logger(__file__)

tablename = envfuncs.get_var('ORDS_DATA')

weights = pd.read_csv(pathfuncs.DATA_DIR +
                      '/ords_category_lca_reference.csv')


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
data['total_weight'] = data.weight * data.records
data['total_emissions'] = (data.footprint * data.records) / 0.5
logger.debug(data)
data.to_csv(pathfuncs.OUT_DIR +
            '/{}_stats_emissions.csv'.format(tablename), index=True)
