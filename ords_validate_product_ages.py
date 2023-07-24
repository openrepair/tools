#!/usr/bin/env python3

from funcs import *
import pandas as pd
logger = logfuncs.init_logger(__file__)

"""
Values in the product_age and year_of_manufacture columns are not always correct.
Often a seemingly impossible product age can mean a vintage or antique device.
Sometimes a value is simply an input error.
See the "How" story in the [data/README.md](data/README.md) about data collection.
Every effort is made to tidy up mistakes at source but it is an ongoing task.
This code can find outliers using a timeline of consumer electronics.
To verify an outlier it is necessary to look at the item type, brand and problem.
"""


# Read the data file as type string with na values set to empty string.
df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                 keep_default_na=False, na_values="")
df.dropna(axis='rows', subset=[
    'year_of_manufacture'], inplace=True, ignore_index=True)

# Convert some of the dtypes as appropriate.
df['product_category_id'] = df['product_category_id'].astype('int64')
df['year_of_manufacture'] = df['year_of_manufacture'].astype('int64')
df['product_age'] = df['product_age'].astype('float64')

df_ref = pd.read_csv(pathfuncs.DATA_DIR + '/consumer_electronics_timeline.csv')

data = pd.DataFrame(df.set_index(['product_category_id', 'product_category']).join(
    df_ref.set_index(['product_category_id', 'product_category'])))

data['is_vintage'] = (data.year_of_manufacture < data.vintage) & (
    data.year_of_manufacture > data.antique)
data['is_antique'] = data.year_of_manufacture <= data.antique

data = data.loc[(data['is_vintage'] == True) | (data['is_antique'] == True)]
logger.debug(data)

data.to_csv(pathfuncs.OUT_DIR +
            '/{}_ords_validate_product_ages.csv'.format(envfuncs.get_var('ORDS_DATA')))
