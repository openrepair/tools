#!/usr/bin/env python3

from funcs import *
import pandas as pd
import deepl
import re

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


# Fetch problem text that has not yet been translated.
# Ignore the more useless values.
# Guess the language for sanity checks later.
def get_work(max=10000, minlen=16):

    print('*** FETCHING WORK ***')
    sql = """
    SELECT t3.id as id_ords, t3.data_provider, t3.country, t3.problem FROM (
    SELECT t2.id_ords, t1.id, t1.data_provider, t1.country, t1.problem
    FROM `{tablename}` t1
    LEFT JOIN ords_problem_translations t2 ON t1.id = t2.id_ords
    UNION ALL
    SELECT t2.id_ords, t1.id, t1.data_provider, t1.country, t1.problem
    FROM `{tablename}` t1
    RIGHT JOIN ords_problem_translations t2 ON t1.id = t2.id_ords
    ) t3
    WHERE t3.id_ords IS NULL
    AND LENGTH(TRIM(t3.problem)) >= {chars}
    LIMIT {limit}
    """
    work = pd.DataFrame(dbfuncs.query_fetchall(sql.format(
        tablename=envfuncs.get_var('ORDS_DATA'), limit=max, chars=minlen)))

    # Assumptions!
    # 99% of the time certain data_providers/countries use a known language.
    # Subject to change, e.g. new Canadian events might use French.
    # "Nonsense" strings with only punctuation or weights/codes dropped.
    work['language_known'] = ''
    filters = {
        0: work['country'].isin(['GBR', 'USA', 'CAN', 'AUS']),
        1: work['country'].isin(['BEL', 'FRA']),
        2: work['country'].isin(['DEU']),
        3: work['country'].isin(['DNK']),
        4: work['country'].isin(['NLD']),
        5: work['problem'].str.fullmatch(
            r'([\W\dkg]+)', flags=re.IGNORECASE+re.UNICODE),
    }
    filterlangs = {
        0: 'en',
        1: 'fr',
        2: 'de',
        3: 'da',
        4: 'nl',
        5: '??',
    }
    logger.debug('*** BEFORE FILTERS ***')
    logger.debug(work)
    for i in range(0, len(filters.keys())):
        print('Applying filter {}'.format(i))
        flt = filters[i]
        dff = work.where(flt)
        dff.dropna(inplace=True)
        dff.language_known = filterlangs[i]
        work.update(dff)
    logger.debug('*** AFTER FILTERS ***')
    logger.debug(work)
    logger.debug('*** AFTER DROPPING ?? ***')
    work.drop(work[work.language_known == '??'].index, inplace=True)
    logger.debug(work)
    return work


def translate(data, langdict):
    sql = """
    SELECT *
    FROM ords_problem_translations
    WHERE problem = %(problem)s
    LIMIT 1
    """
    try:
        # For each record fetch a translation for each target language.
        for i, row in data.iterrows():
            # Is there already a translation for this text?
            found = pd.DataFrame(dbfuncs.query_fetchall(
                sql,  {'problem': row.problem}))
            if found.empty:
                # No existing translation so fetch from API.
                d_lang = False
                for column in langdict.keys():
                    t_lang = langdict[column]
                    print('{} : {} : {}'.format(i, row.id_ords, t_lang))
                    # Has a language been detected for this problem?
                    # Is the target language the same as the detected language?
                    if d_lang == t_lang:
                        # Don't use up API credits.
                        text = row.problem
                    else:
                        # No existing translation so fetch from API.
                        logger.debug(
                            '{} is new... translating'.format(row.id_ords))
                        try:
                            result = translator.translate_text(
                                row.problem, target_lang=t_lang)
                            d_lang = result.detected_source_lang.lower()
                            text = result.text
                        except deepl.DeepLException as error:
                            print("exception: {}".format(error))
                            data.at[i, 'language_detected'] = ''
                            return data

                    data.at[i, 'translator'] = 'DeepL'
                    data.at[i, 'language_detected'] = d_lang
                    data.at[i, column] = text
            else:
                # Translation exists so copy from existing.
                logger.debug('{} exists... copying'.format(row.id_ords))
                data.at[i, 'language_known'] = found.language_known.values[0]
                data.at[i, 'translator'] = found.translator.values[0]
                data.at[i, 'language_detected'] = found.language_detected.values[0]
                for column in langdict.keys():
                    data.at[i, column] = found[column].values[0]

    except Exception as error:
        print("Exception: {}".format(error))

    finally:
        return data


def insert_data(data):

    if 'language_detected' in data.columns:
        data = data.loc[data.language_detected > '']
    else:
        print('No data to write.')
        return False

    if data.empty:
        print('No data to write.')
        return False

    cfile = pathfuncs.OUT_DIR + '/deepl_latest.csv'
    pathfuncs.rm_file(cfile)
    data.to_csv(cfile, index=False)
    print('New data written to {}'.format(cfile))

    rows = data.to_sql(name='ords_problem_translations', con=dbfuncs.alchemy_eng(),
                       if_exists='append', index=False)
    logger.debug('{} rows written to table {}'.format(
        rows, 'ords_problem_translations'))

    return True


# START

# Allows for trial and error without using up API credits.
# Should create a test and use mock there, ideally.
mock = True
translator = deeplfuncs.deeplWrapper(mock)

# 5-10k recommended for live run.
work = get_work(1000)
work.to_csv(pathfuncs.OUT_DIR + '/deepl_work.csv', index=False)

if translator.api_limit_reached():
    exit()
else:
    data = translate(work, deeplfuncs.deeplWrapper.langdict)
    if not mock:
        insert_data(data)
        dbfuncs.dump_table_to_csv(
            'ords_problem_translations', pathfuncs.DATA_DIR)
    else:
        logger.debug(data)