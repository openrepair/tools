#!/usr/bin/env python3

from funcs import *
import pandas as pd
import datetime
from datetime import datetime

logger = logfuncs.init_logger(__file__)

"""
Values in the product_age and year_of_manufacture columns are not always correct.
Often a seemingly impossible product age can mean a vintage or antique device.
Sometimes a value is simply an input error.
See the "How" story in the [data/README.md](data/README.md) about data collection.
Every effort is made to tidy up mistakes at source but it is an ongoing task.
This code can find outliers using a timeline of consumer electronics.
To truly verify an outlier it is necessary to look at the item type, brand and problem.
This script also flags vintage, antique and recent devices.
"""

# Read the ORDS data.
df_in = pd.read_csv(pathfuncs.path_to_ords_csv())
df_in.dropna(axis='rows', subset=[
    'year_of_manufacture'], inplace=True, ignore_index=True)
# Misc records have no timeline data.
df_in = df_in.loc[df_in.product_category != 'Misc']
# Uncomment if only interested in success stories.
# df_in = df_in.loc[df_in.repair_status.isin(['Fixed', 'Repairable'])]

# Convert string to date so year can be extracted.
df_in['event_date'] = pd.to_datetime(df_in['event_date'])

# Read the timeline data.
df_ref = pd.read_csv(pathfuncs.DATA_DIR + '/consumer_electronics_timeline.csv')
# In case any year values are missing.
df_ref.dropna(axis='rows', subset=[
    'earliest'], inplace=True, ignore_index=True)

# Join the two frames.
data = df_in.join(df_ref.set_index('product_category_id'),
                  on='product_category_id', rsuffix='_')
data.drop(columns=['product_category_'], inplace=True)

# Assumptions that can be changed.
# 1. vintage cut-off is halfway between current year minus earliest year
# 2. recent year is between current year and 10 years previous
curr_year = datetime.now().year
dict = {'year_event': 0,
    'year_recent': 0,
    'year_vintage': 0,
    'is_impossible': False,
    'is_mistake': False,
    'is_vintage': False,
    'is_antique': False,
    'is_recent': False}
cols = sorted(list(set(list(data.columns)+list(dict.keys()))))
df_out = pd.DataFrame(columns=cols)
rowlist = []
for i, row in data.iterrows():
    try:
        d = row.to_dict() | dict
        d['year_curr'] = curr_year
        d['year_event'] = row.event_date.year
        d['year_recent'] = curr_year-10
        d['year_vintage'] = round(d['year_curr']-((d['year_curr']-row.earliest)/2))
        if row.year_of_manufacture >= d['year_event']:
            d['is_mistake'] = True
        elif (row.year_of_manufacture <= row.earliest) & (row.year_of_manufacture > d['year_curr']):
            d['is_impossible'] = True
        elif row.year_of_manufacture >= d['year_recent']:
            d['is_recent'] = True
        elif row.year_of_manufacture <= d['year_vintage']:
            d['is_vintage'] = True
        elif (row.year_of_manufacture >= d['year_vintage']) & (row.year_of_manufacture <= d['year_recent']):
            d['is_antique'] = True
        else:
            logger.debug('???????')
            logger.debug(d)
        rowlist.append(d)
    except Exception as error:
        print(row)
        print(error)
        continue


df_out = pd.concat([df_out, pd.DataFrame(data=rowlist, columns=cols)])
df_out.sort_values(by=['product_category'],
                   ascending=True, inplace=True, ignore_index=True)

df_1 = df_out.loc[(df_out['is_vintage'] == True) |
                    (df_out['is_antique'] == True)]
df_1.to_csv(pathfuncs.OUT_DIR +
              '/{}_product_ages_vintage.csv'.format(envfuncs.get_var('ORDS_DATA')), index=False)

df_2 = df_out.loc[(df_out['is_impossible'] == True) |
                    (df_out['is_mistake'] == True)]
df_2.to_csv(pathfuncs.OUT_DIR +
              '/{}_product_ages_impossible.csv'.format(envfuncs.get_var('ORDS_DATA')), index=False)
