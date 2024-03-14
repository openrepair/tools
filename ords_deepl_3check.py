#!/usr/bin/env python3

from funcs import *
import pandas as pd

logger = logfuncs.init_logger(__file__)

"""
Series of scripts for translating ORDS `problem` text.

https://github.com/DeepLcom/deepl-python

Step 1: ords_deepl_1setup.py
    Table created, MySQL database required.
Step 2: ords_deepl_2fetch.py
    Compiles workload, translates, DeepL API key required.
Step 3: ords_deepl_3check.py
    Inspect data integrity.
Step 4: ords_deepl_4backfill.py
    Translate missing values for given languages.
"""


# Language detection stats.
logger.debug("*** DETECTED ***")
sql = """
    SELECT language_detected, COUNT(*) as records
    FROM `ords_problem_translations`
    GROUP BY language_detected
    ORDER BY records DESC
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
logger.debug(df)


# Outlier languages detected.
logger.debug("*** UNKNOWN LANGUAGE DETECTED***")
sql = """
    SELECT language_known, language_detected, COUNT(*) as records
    FROM `ords_problem_translations`
    WHERE language_detected NOT IN ('??', 'en', 'de', 'nl', 'fr', 'it', 'es', 'da')
    GROUP BY language_known, language_detected
    ORDER BY records DESC
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
logger.debug(df)


# Detected language does not match "known" language.
# Note that "known" language could be incorrect.
# Log summary and write to csv file.
logger.debug("*** MISMATCHED LANGUAGE DETECTION ***")
path = pathfuncs.OUT_DIR + "/deepl_misdetect.csv"
logger.debug("See " + path)
sql = """
    SELECT language_known, language_detected, COUNT(*) as records
    FROM `ords_problem_translations`
    WHERE language_detected != language_known
    GROUP BY language_known, language_detected
    ORDER BY records DESC
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
logger.debug(df)
sql = """
    SELECT id_ords, language_known, language_detected, problem
    FROM `ords_problem_translations`
    WHERE language_detected != language_known
    ORDER BY language_known, language_detected
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
df.to_csv(path, index=False)


# Identical translations across languages.
# Could be bad language detected or malformed problem text.
# Write results to csv file.
logger.debug("*** IDENTICAL TRANSLATIONS ***")
path = pathfuncs.OUT_DIR + "/deepl_mistranslate.csv"
logger.debug("See " + path)
sql = """
    SELECT id_ords, language_known, language_detected,
    en, de, nl, fr, it, es, da
    FROM `ords_problem_translations`
    WHERE language_detected <> '??'
    AND (`en` = `problem`
    AND `de` = `problem`
    AND `nl` = `problem`
    AND `fr` = `problem`
    AND `it` = `problem`
    AND `es` = `problem`
    AND `da` = `problem`)
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
df.to_csv(path, index=False)


# Missing translations across languages.
# Could have run out of DeepL credits before lang set completion.
# Write results to csv file.
logger.debug("*** MISSING TRANSLATIONS ***")
path = pathfuncs.OUT_DIR + "/deepl_missing.csv"
logger.debug("See " + path)
sql = """
    SELECT id_ords, language_known, language_detected,
    en, de, nl, fr, it, es, da
    FROM `ords_problem_translations`
    WHERE CONCAT(`en`,`de`,`nl`,`fr`,`it`,`es`,`da`) IS NULL
    OR (`en` = '' OR `de` = '' OR `nl` = '' OR `fr` = '' OR `it` = '' OR `es` = '' OR `da` = '');
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
df.to_csv(path, index=False)

