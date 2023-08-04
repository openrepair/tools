#!/usr/bin/env python3

import pandas as pd
from funcs import *
logger = logfuncs.init_logger(__file__)

# Creates and populates tables with ORDS data.

table_cats = envfuncs.get_var('ORDS_CATS')
table_data = envfuncs.get_var('ORDS_DATA')

# Get db table schemas. (Not the same as ORDS CSV schema)
path = pathfuncs.get_path([pathfuncs.DATA_DIR, 'tableschema_ords_mysql.sql'])
logger.debug('Reading file "{}"'.format(path))
sql = path.read_text().format(table_cats, table_data)

# Set up tables
dbfuncs.execute(sql)

# Import ORDS product_category values.
path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table_cats + '.csv'])
logger.debug('Reading file "{}"'.format(path))
dfcats = pd.read_csv(path)
rows = dfcats.to_sql(name=table_cats, con=dbfuncs.alchemy_eng(),
                     if_exists='append', index=False)
logger.debug('{} written to table "{}"'.format(rows, table_cats))

# Import ORDS data.
path = pathfuncs.get_path([pathfuncs.ORDS_DIR, table_data + '.csv'])
logger.debug('Reading file "{}"'.format(path))
dfdata = pd.read_csv(path)
rows = dfdata.to_sql(name=table_data, con=dbfuncs.alchemy_eng(),
                     if_exists='append', index=False)
logger.debug('{} written to table "{}"'.format(rows, table_data))
