#!/usr/bin/env python3

from funcs import *
import pandas as pd
import deepl
import re

logger = logfuncs.init_logger(__file__)

# Step 1: ords_deepl_setup.py
# Step 2: ords_deepl_fetch.py
# https://github.com/DeepLcom/deepl-python


def limit_reached():
    usage = translator.get_usage()
    if usage.character.valid:
        print(
            f"Character usage: {usage.character.count} of {usage.character.limit}")
    if usage.any_limit_reached:
        print('Translation limit reached.')
        return True
    return False


def get_work(max=10000):

    print('*** FETCHING FROM DB ***')
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
    AND TRIM(t3.problem) > ''
    LIMIT {limit}
    """
    work = pd.DataFrame(dbfuncs.query_fetchall(sql.format(
        tablename=envfuncs.get_var('ORDS_DATA'), limit=max)))

    # Assumptions!
    # 99% of the time certain data_providers/countries use a known language.
    # Subject to change, e.g. new Canadian events might use French.
    # "Nonsense" strings with only punctuation or weights/codes flagged with '??'
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
    print('*** APPLYING FILTERS ***')
    for i in range(0, len(filters.keys())):
        print(i)
        flt = filters[i]
        dff = work.where(flt)
        dff.dropna(inplace=True)
        dff.language_known = filterlangs[i]
        logger.debug(dff)
        work.update(dff)
    return work


# Mock DeepL result class for testing
class MockDeepLResult:
    def __init__(self):
        self.detected_source_lang = miscfuncs.randstr(len=2, up=True)
        self.text = miscfuncs.randstr()


def translate(data):
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
                for t_lang in langs:
                    print('{} : {}'.format(i, t_lang))
                    # Has a language been detected for this problem?
                    # Is the target language the same as the detected language?
                    if d_lang == t_lang:
                        # Don't use up API credits.
                        text = row.problem
                    else:
                        # No existing translation so fetch from API.
                        try:
                            key = t_lang.rstrip("-gb")
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
                    data.at[i, key] = text
            else:
                # Translation exists so copy from existing.
                data.at[i, 'language_known'] = found.language_known.values[0]
                data.at[i, 'translator'] = found.translator.values[0]
                data.at[i, 'language_detected'] = found.language_detected.values[0]
                for t_lang in langs:
                    key = t_lang.rstrip("-gb")
                    data.at[i, key] = found[key].values[0]

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


def dump_data():
    sql = """
    SELECT *
    FROM ords_problem_translations
    """
    df = pd.DataFrame(dbfuncs.query_fetchall(sql))
    path_to_csv = pathfuncs.DATA_DIR + '/ords_problem_translations.csv'
    df.to_csv(path_to_csv, index=False)
    if pathfuncs.check_path(path_to_csv):
        print('Data dumped to {}'.format(path_to_csv))
        return path_to_csv
    else:
        print('Failed to dump data to {}'.format(path_to_csv))
        return False

# START


# To Do: add Danish translations to 'da' column.
langs = ['en-gb', 'de', 'nl', 'fr', 'it', 'es']

# 10k recommended
work = get_work(10)
work.to_csv(pathfuncs.OUT_DIR + '/deepl_work.csv', index=False)

if auth_key := envfuncs.get_var('DEEPL_KEY'):
    translator = deepl.Translator(auth_key)
else:
    print('Add your DeepL API key to the .env file.')
    exit()

if limit_reached():
    exit()
else:
    data = translate(work)
    insert_data(data)
    dump_data()
