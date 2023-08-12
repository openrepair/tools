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
    ORDER BY t3.country
    LIMIT {limit}
    """
    work = pd.DataFrame(dbfuncs.query_fetchall(sql.format(
        tablename=envfuncs.get_var('ORDS_DATA'), limit=max, chars=minlen)))

    # "Nonsense" strings with only punctuation or weights/codes dropped.
    # Assumptions!
    # 99% of the time certain data_providers/countries use a known language.
    # Some countries return multiple language texts:
    # Belgium: French and Dutch.
    # Canada: French and English.
    # Italy: Italian and English.
    work['language_known'] = ''
    work['language_expected'] = ''
    filters = {
        1: work['country'].isin(['GBR', 'USA', 'AUS', 'NZL', 'IRL', 'ISR', 'ZAF', 'SWE', 'NOR', 'HKG', 'JEY', 'TUN', 'ISL']),
        2: work['country'].isin(['FRA']),
        3: work['country'].isin(['DEU']),
        4: work['country'].isin(['DNK']),
        5: work['country'].isin(['NLD']),
        6: work['country'].isin(['ESP']),
    }
    filterlangs = {
        1: 'en',
        2: 'fr',
        3: 'de',
        4: 'da',
        5: 'nl',
        6: 'es',
    }
    logger.debug('*** BEFORE FILTERS ***')
    logger.debug(work)
    for i in range(1, len(filters.keys())):
        print('Applying filter {}'.format(i))
        flt = filters[i]
        dff = work.where(flt)
        dff.dropna(inplace=True)
        dff.language_expected = filterlangs[i]
        work.update(dff)

    logger.debug('*** FILTERING PUNCT/WEIGHTS/CODES ***')
    # Filter for punctuation/weights/codes.
    flt = work['problem'].str.fullmatch(
        r'([\W\dkg]+)', flags=re.IGNORECASE+re.UNICODE)
    dff = work.where(flt)
    dff.dropna(inplace=True)
    dff.language_expected = '??'
    logger.debug(dff)
    work.update(dff)

    logger.debug('*** AFTER FILTERS ***')
    logger.debug(work)
    logger.debug('*** AFTER DROPPING ?? ***')
    work.drop(work[work.language_expected == '??'].index, inplace=True)
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
                # Use the known language as source else let DeepL detect.
                if row.language_known > '':
                    k_lang = row.language_known
                else:
                    k_lang = None

                for column in langdict.keys():
                    t_lang = langdict[column]
                    print('{} : {} : {} : {}'.format(
                        i, row.id_ords, k_lang, t_lang))
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
                                row.problem, target_lang=t_lang, source_lang=k_lang)
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


# Use a pre-trained model to detect and set the 'known language'.
# This should be more accurate than DeepL's language detection, though model still being refined.
# Requires that `ords_lang_training.py` has created the model object.
def detect_language(data):

    from joblib import load
    path = pathfuncs.OUT_DIR + '/ords_lang_obj_tfidf_cls.joblib'
    if not pathfuncs.check_path(path):
        print('Model object not found at {}'.format(path))
    else:
        model = load(path)
        # Use `language_known` as source lang for DeepL translations.
        # Use `language_expected` for checking DeepL language detection.
        # Adjust filters in get_work() and retrain model as appropriate.
        data.loc[:, 'language_known'] = model.predict(data.problem)

    data.loc[:, 'mismatch'] = data['language_expected'] != data['language_known']

    # Log the mismatches.
    miss = data.loc[work['mismatch'] == True]
    miss.to_csv(pathfuncs.OUT_DIR +
                '/deepl_work_lang_mismatch.csv', index=False)
    # Count the mismatches.
    grp = miss.groupby('country').agg({'mismatch': ['count']}).pipe(lambda x: x.set_axis(
        x.columns.map('_'.join), axis=1)).sort_values(by='mismatch_count', ascending=False)
    logger.debug(grp)

    return data


# START


# Allows for trial and error without using up API credits.
# Should create a test and use mock there, ideally.
mock = True
translator = deeplfuncs.deeplWrapper(mock)

# 5-10k recommended for live run.
work = get_work(10)
work = detect_language(data=work)
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
