#!/usr/bin/env python3

import pandas as pd
from funcs import *
logger = logfuncs.init_logger(__file__)

# Step 1: ords_deepl_setup.py
# Step 2: ords_deepl_fetch.py
# Step 3: ords_deepl_misc.py
# https://github.com/DeepLcom/deepl-python

def bad_detections():

    sql = """
    SELECT language_detected, COUNT(*) as records
    FROM `ords_problem_translations`
    GROUP BY language_detected
    ORDER BY records DESC
    """
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql))
    df_res.to_csv(pathfuncs.OUT_DIR + '/deepl_lang_detect.csv', index=False)

    sql = """
    SELECT *
    FROM `ords_problem_translations`
    WHERE UPPER(language_detected) NOT IN ('en', 'en-gb', 'de', 'nl', 'fr', 'it', 'es')
    """
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql))
    df_res.to_csv(pathfuncs.OUT_DIR + '/deepl_bad_detect.csv', index=False)


# START

bad_detections()
