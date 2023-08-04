#!/usr/bin/env python3

from funcs import *
import pandas as pd
import deepl

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
# Arg 'cols' is a list of columns to check.
def get_work_for_null_lang_vals(cols, max=100):
    print('*** FETCHING WORK FOR EMPTY LANGUAGE VALUES ***')
    sql = """
    SELECT *
    FROM ords_problem_translations
    WHERE language_known <> '??'
    AND CONCAT({}) IS NULL
    LIMIT {}
    """.format(','.join(cols), max)
    work = pd.DataFrame(dbfuncs.query_fetchall(sql.format(
        tablename=envfuncs.get_var('ORDS_DATA'))))
    return work


def translate_empty_only(data, langdict):
    try:
        # For each record fetch a translation for each target language where empty.
        for i, row in data.iterrows():
            # The "detected" language is the known language
            d_lang = row.language_known
            for column in langdict.keys():
                t_lang = langdict[column]
                if row[column] == None:
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
                                row.problem, target_lang=t_lang, source_lang=row.language_known)
                            text = result.text
                        except deepl.DeepLException as error:
                            print("exception: {}".format(error))
                            data.at[i, 'language_detected'] = ''
                            return data

                    data.at[i, column] = text

    except Exception as error:
        print("Exception: {}".format(error))

    finally:
        return data


def insert_data(data, columns):

    if data.empty:
        print('No data to write.')
        return False

    # Assumption:
    # If single column only, don't update whole row.
    # Else, update whole row.
    if len(columns) == 1:
        column = columns.pop()
        cfile = pathfuncs.OUT_DIR + \
            '/deepl_backfilled_lang_{}.csv'.format(column)
        vals = list(zip(data[column], data['id_ords']))
        sql = """UPDATE `ords_problem_translations` SET `{}`=%s WHERE id_ords=%s"""
        rows = dbfuncs.executemany(sql.format(column), vals)
    else:
        cfile = pathfuncs.OUT_DIR + '/deepl_backfilled_lang_all.csv'
        vals = list(zip(*[data[col] for col in data]))
        logger.debug(vals)
        sql = """REPLACE INTO `ords_problem_translations` (`{}`) VALUES ({})""".format(
            "`,`".join(data.columns), ",".join(["%s"] * len(data.columns)))
        logger.debug(sql)
        rows = dbfuncs.executemany(sql, vals)

    logger.debug('{} rows written to table {}'.format(
        rows, 'ords_problem_translations'))
    pathfuncs.rm_file(cfile)
    data.to_csv(cfile, index=False)
    print('New data written to {}'.format(cfile))

    return True


# START

# Allows for trial and error without using up API credits.
# Should create a test and use mock there, ideally.
mock = True
translator = deeplfuncs.deeplWrapper(mock)
"""
Get the columns to check for NULL values. Examples:
Just one column.
filter = ['da']
Selection of columns.
filter = ['it','es']
All columns.
filter = deeplfuncs.deeplWrapper.get_columns()
All but the last column.
filter = [x for x in deeplfuncs.deeplWrapper.get_columns()[:-1]]
"""
filter = [x for x in deeplfuncs.deeplWrapper.get_columns()[:-1]]
# Currently backfilling for all but Danish
# Then will backfill only Danish
work = get_work_for_null_lang_vals(filter, 1)
work.to_csv(pathfuncs.OUT_DIR + '/deepl_backfill_work.csv', index=False)

if translator.api_limit_reached():
    exit()
else:
    data = translate_empty_only(work, deeplfuncs.deeplWrapper.langdict)
    if not mock:
        insert_data(data)
        dbfuncs.dump_table_to_csv(
            'ords_problem_translations', pathfuncs.DATA_DIR)
    else:
        logger.debug(data)
