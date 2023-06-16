#!/usr/bin/env python3

from funcs import *
import pandas as pd
logger = logfuncs.init_logger(__file__)

# Based on the LCA Reference data published by The Restart Project under a Creative Commons license (CC BY-SA 4.0) in 2021.
# With thanks to James Pickstone and a team of volunteers!
# [The environmental impact of our devices: revealing what many companies hide](https://therestartproject.org/consumption/hidden-impact-devices/)
# [Fixometer reference data - 2021 ](https://docs.google.com/spreadsheets/d/1TBhczzDaJhANTMh3eoouMOFZ7PvlmyrEQMqnw9WfdHY/edit?usp=sharing)

table_data = envfuncs.get_var('ORDS_DATA')
weights = pd.read_csv(pathfuncs.DATA_DIR +
                      '/ords_category_lca_reference.csv')

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
    sql.format(table_data))).set_index('product_category').join(
    weights.set_index('product_category'))
data['total_weight'] = data.weight * data.records
data['total_emissions'] = (data.footprint * data.records) / 0.5
logger.debug(data)
data.to_csv(pathfuncs.OUT_DIR +
            '/ords_stats_emissions.csv', index=False)
