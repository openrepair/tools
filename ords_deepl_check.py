#!/usr/bin/env python3

from funcs import *
import pandas as pd

logger = logfuncs.init_logger(__file__)

# Check the outcome of DeepL translations.

# Language detection stats.
logger.debug('*** DETECTED ***')
sql = """
    SELECT language_detected, COUNT(*) as records
    FROM `ords_problem_translations`
    GROUP BY language_detected
    ORDER BY records DESC
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
logger.debug(df)


# Outlier languages detected.
logger.debug('*** UNKNOWN LANGUAGE DETECTED***')
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
logger.debug('*** MISMATCHED LANGUAGE DETECTION ***')
path = pathfuncs.OUT_DIR + '/deepl_misdetect.csv'
logger.debug('See ' + path)
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
logger.debug('*** IDENTICAL TRANSLATIONS ***')
path = pathfuncs.OUT_DIR + '/deepl_mistranslate.csv'
logger.debug('See ' + path)
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
    AND `es` = `problem`)
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
df.to_csv(path, index=False)


# Missing translations across languages.
# Could have run out of DeepL credits before lang set completion.
# Write results to csv file.
logger.debug('*** MISSING TRANSLATIONS ***')
path = pathfuncs.OUT_DIR + '/deepl_missing.csv'
logger.debug('See ' + path)
sql = """
    SELECT id_ords, language_known, language_detected,
    en, de, nl, fr, it, es, da
    FROM `ords_problem_translations`
    WHERE CONCAT(`en`,`de`, `nl`, `fr`, `it`, `es`) IS NULL;
    """
df = pd.DataFrame(dbfuncs.query_fetchall(sql))
df.to_csv(path, index=False)

