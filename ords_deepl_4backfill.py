#!/usr/bin/env python3

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

from funcs import *
import pandas as pd
import deepl


def find_existing_translation_for_col(problem, column):
    sql = """
    SELECT problem, {0}, COUNT(*) as records
    FROM ords_problem_translations
    WHERE problem = %(problem)s
    AND {0} IS NOT NULL
    GROUP BY problem, {0}
    HAVING records > 1
    ORDER BY records DESC
    LIMIT 1;
    """.format(
        column
    )
    work = pd.DataFrame(
        dbfuncs.query_fetchall(
            sql.format(tablename=envfuncs.get_var("ORDS_DATA")), {"problem": problem}
        )
    )
    return work


# Fetch problem text that has not yet been translated.
# Ignore the more useless values.
# Arg 'cols' is a list of columns to check.
def get_work_for_null_lang_vals(cols, max=100):
    try:
        print("*** FETCHING WORK FOR EMPTY LANGUAGE VALUES ***")
        sql = """
        SELECT *
        FROM ords_problem_translations
        WHERE language_known <> '??'
        AND CONCAT({}) IS NULL
        LIMIT {}
        """.format(
            ",".join(cols), max
        )
        logger.debug(sql)
        work = pd.DataFrame(
            dbfuncs.query_fetchall(sql.format(tablename=envfuncs.get_var("ORDS_DATA")))
        )
    except Exception as error:
        print("Exception: {}".format(error))
        work = pd.DataFrame()
    finally:
        return work


def translate_empty_only(data, langdict):
    try:
        # For each record fetch a translation for each target language where empty.
        for i, row in data.iterrows():
            d_lang = row.language_known
            for column in langdict.keys():
                # Is there already a translation for this text?
                found = find_existing_translation_for_col(row.problem, column)
                if found.empty:
                    # No existing translation so fetch from API.
                    # The "detected" language is the known language
                    if row[column] == None:
                        t_lang = langdict[column]
                        print("{} : {} : {}".format(i, row.id_ords, t_lang))
                        # Has a language been detected for this problem?
                        # Is the target language the same as the detected language?
                        if d_lang == t_lang:
                            # Don't use up API credits.
                            text = row.problem
                        else:
                            # No existing translation so fetch from API.
                            logger.debug("{} is new... translating".format(row.id_ords))
                            try:
                                result = translator.translate_text(
                                    row.problem,
                                    target_lang=t_lang,
                                    source_lang=row.language_known,
                                )
                                text = result.text
                            except deepl.DeepLException as error:
                                print("exception: {}".format(error))
                                return data

                        data.at[i, column] = text
                else:
                    # Translation exists so copy from existing.
                    logger.debug("{} exists... copying".format(row.id_ords))
                    data.at[i, column] = found[column].values[0]

    except Exception as error:
        print("Exception: {}".format(error))

    finally:
        return data


# Default: replace entire row.
# Or single element list e.g.: ['fr'], replace one column only.
def insert_data(data, columns=[]):

    if data.empty:
        print("No data to write.")
        return False

    if len(columns) == 1:
        column = columns.pop()
        cfile = pathfuncs.OUT_DIR + "/deepl_backfilled_lang_{}.csv".format(column)
        vals = list(zip(data[column], data["id_ords"]))
        sql = """UPDATE `ords_problem_translations` SET `{}`=%s WHERE id_ords=%s"""
        result = dbfuncs.executemany(sql.format(column), vals)
    else:
        cfile = pathfuncs.OUT_DIR + "/deepl_backfilled_lang_all.csv"
        vals = list(zip(*[data[col] for col in data]))
        logger.debug(vals)
        sql = """REPLACE INTO `ords_problem_translations` (`{}`) VALUES ({})""".format(
            "`,`".join(data.columns), ",".join(["%s"] * len(data.columns))
        )
        logger.debug(sql)
        result = dbfuncs.executemany(sql, vals)

    logger.debug("{} updated in {}".format(result, "ords_problem_translations"))
    pathfuncs.rm_file(cfile)
    data.to_csv(cfile, index=False)
    print("New data written to {}".format(cfile))

    return True


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    # Allows for trial and error without using up API credits.
    # Should create a test and use mock there, ideally.
    mock = True
    translator = deeplfuncs.deeplWrapper(mock)
    limit_reached = translator.api_limit_reached()
    """
    Get the columns to check for NULL values. Examples:
    Just one column.
    columns = ['da']
    Selection of columns.
    columns = ['it','es']
    All columns.
    columns = deeplfuncs.deeplWrapper.get_columns()
    All but the last column.
    columns = [x for x in deeplfuncs.deeplWrapper.get_columns()[:-1]]
    """
    # Backfilling for all
    columns = deeplfuncs.deeplWrapper.get_columns()
    limit = 10000
    work = get_work_for_null_lang_vals(columns, limit)
    print(work.count())
    logger.debug(work.count())
    work.to_csv(pathfuncs.OUT_DIR + "/deepl_backfill_work.csv", index=False)

    if limit_reached:
        exit()
    else:
        # Backfilling any empty columns: deeplfuncs.deeplWrapper.langdict
        # Backfilling one column only, e.g. Danish: {'da':'da'}
        data = translate_empty_only(work, deeplfuncs.deeplWrapper.langdict)
        data.to_csv(pathfuncs.OUT_DIR + "/deepl_backfill_latest.csv", index=False)
        if not mock:
            insert_data(data, columns)
            dbfuncs.dump_table_to_csv("ords_problem_translations", pathfuncs.DATA_DIR)
        else:
            logger.debug(data)
