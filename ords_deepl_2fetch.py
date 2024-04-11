#!/usr/bin/env python3

from funcs import *
from joblib import load
import pandas as pd
import deepl
import re

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
def get_work(max=10000, minlen=16, clause=1, lang=None):

    # Check for valid language code.
    if lang != None:
        langdict = deeplfuncs.deeplWrapper.langdict
        if lang not in langdict.keys():
            print("INVALID LANGUAGE CODE {}".format(lang))
            exit()

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
    AND LENGTH(TRIM(t3.problem)) >= %(chars)s
    AND {clause}
    ORDER BY t3.country
    LIMIT %(limit)s
    """
    args = {"limit": max, "chars": minlen}
    work = pd.DataFrame(
        dbfuncs.query_fetchall(
            sql.format(tablename=envfuncs.get_var("ORDS_DATA"), clause=clause), args
        )
    )

    # "Nonsense" strings with only punctuation or weights/codes dropped.
    # Assumptions!
    # 99% of the time certain data_providers/countries use a known language.
    # Some countries return multiple language texts:
    # Belgium: French and Dutch.
    # Canada: French and English.
    # Italy: Italian and English.
    # Many countries have a little English sprinkled in.
    # These assumptions can be overwritten by detect_language() see below.
    work["language_known"] = ""
    work["language_expected"] = ""
    filters = {
        1: work["country"].isin(
            [
                "GBR",
                "USA",
                "AUS",
                "NZL",
                "IRL",
                "ISR",
                "ZAF",
                "SWE",
                "NOR",
                "HKG",
                "JEY",
                "TUN",
                "ISL",
            ]
        ),
        2: work["country"].isin(["FRA"]),
        3: work["country"].isin(["DEU"]),
        4: work["country"].isin(["DNK"]),
        5: work["country"].isin(["NLD"]),
        6: work["country"].isin(["ESP"]),
    }
    filterlangs = {
        1: "en",
        2: "fr",
        3: "de",
        4: "da",
        5: "nl",
        6: "es",
    }
    logger.debug("*** BEFORE FILTERS ***")
    logger.debug(work)
    for i, flt in filters.items():
        dff = work.where(flt)
        dff.dropna(inplace=True)
        if dff.size > 0:
            dff.language_expected = filterlangs[i]
            work.update(dff)
            dff.to_csv(
                pathfuncs.OUT_DIR + "/deepl_work_filter_{}.csv".format(i), index=False
            )

    logger.debug("*** AFTER FILTERS ***")
    logger.debug(work)

    logger.debug("*** FILTERING PUNCT/WEIGHTS/CODES ***")
    # Filter for punctuation/weights/codes.
    flt = work["problem"].str.fullmatch(
        r"([\W\dkg]+)", flags=re.IGNORECASE + re.UNICODE
    )
    dff = work.where(flt)
    dff.dropna(inplace=True)
    dff.language_expected = "??"
    logger.debug(dff)
    work.update(dff)

    logger.debug("*** AFTER DROPPING ?? ***")
    work.drop(work[work.language_expected == "??"].index, inplace=True)
    logger.debug(work)

    if lang != None:
        work.loc[:, "language_known"] = lang
    else:
        work = detect_language(data=work)
    logger.debug(work)
    work.to_csv(pathfuncs.OUT_DIR + "/deepl_work.csv", index=False)
    return work


def translate(data, mock=True):
    translator = deeplfuncs.deeplWrapper(mock)
    langdict = deeplfuncs.deeplWrapper.langdict
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
            found = pd.DataFrame(dbfuncs.query_fetchall(sql, {"problem": row.problem}))
            if found.empty:
                # No existing translation so fetch from API.
                d_lang = None
                # Use the known language as source else let DeepL detect.
                if row.language_known > "":
                    k_lang = row.language_known
                else:
                    k_lang = None

                for column in langdict.keys():
                    # Get the target language for Deepl.
                    t_lang = langdict[column]
                    print("{} : {} : {} : {}".format(i, row.id_ords, k_lang, t_lang))
                    # Has a language been detected for this problem?
                    # Is the target language the same as the known language?
                    if column == k_lang:
                        # Don't use up API credits.
                        text = row.problem
                    else:
                        # No existing translation so fetch from API.
                        logger.debug("{} is new... translating".format(row.id_ords))
                        try:
                            result = translator.translate_text(
                                row.problem, target_lang=t_lang, source_lang=k_lang
                            )
                            d_lang = result.detected_source_lang.lower()
                            text = result.text
                        except deepl.DeepLException as error:
                            print("exception: {}".format(error))
                            data.at[i, "language_detected"] = ""
                            return data

                    data.at[i, "translator"] = "DeepL"
                    data.at[i, "language_detected"] = d_lang
                    data.at[i, column] = text
            else:
                # Translation exists so copy from existing.
                logger.debug("{} exists... copying".format(row.id_ords))
                data.at[i, "language_known"] = found.language_known.values[0]
                data.at[i, "translator"] = found.translator.values[0]
                data.at[i, "language_detected"] = found.language_detected.values[0]
                for column in langdict.keys():
                    data.at[i, column] = found[column].values[0]

    except Exception as error:
        print("Exception: {}".format(error))

    finally:
        return data


def insert_data(data):

    if "language_detected" in data.columns:
        data = data.loc[data.language_detected > ""]
    else:
        print("No data to write.")
        return False

    if data.empty:
        print("No data to write.")
        return False

    # Drop redundant columns used for testing expectations.
    if "language_expected" in data.columns:
        data.drop(["language_expected"], axis=1, inplace=True)
    if "mismatch" in data.columns:
        data.drop(["mismatch"], axis=1, inplace=True)

    cfile = pathfuncs.OUT_DIR + "/deepl_latest.csv"
    pathfuncs.rm_file(cfile)
    data.to_csv(cfile, index=False)
    print("New data written to {}".format(cfile))

    rows = data.to_sql(
        name="ords_problem_translations",
        con=dbfuncs.alchemy_eng(),
        if_exists="append",
        index=False,
    )
    logger.debug(
        "{} rows written to table {}".format(rows, "ords_problem_translations")
    )

    return True


# Use a pre-trained model to detect and set the 'known language'.
# This should be more accurate than DeepL's language detection, though model still being refined.
def detect_language(data):

    lang_obj_path = pathfuncs.OUT_DIR + "/ords_lang_obj_tfidf_cls_sentence.joblib"
    if not pathfuncs.check_path(lang_obj_path):
        print("LANGUAGE DETECTOR ERROR: MODEL NOT FOUND at {}".format(lang_obj_path))
        print("TO FIX THIS EXECUTE: ords_lang_training_sentence.py")
        exit()

    model = load(lang_obj_path)
    # Use `language_known` as source lang for DeepL translations.
    # Use `language_expected` for checking DeepL language detection.
    # Adjust filters in get_work() and retrain model as appropriate.
    data.loc[:, "language_known"] = model.predict(data.problem)

    # `language_expected` is based on familiar assumptions about the data and may be empty.
    data.loc[:, "mismatch"] = data["language_expected"] != data["language_known"]

    # Log the mismatches.
    miss = data.loc[data["mismatch"] == True]
    miss.to_csv(pathfuncs.OUT_DIR + "/deepl_work_lang_mismatch.csv", index=False)
    # Count the mismatches.
    grp = (
        miss.groupby("country")
        .agg({"mismatch": ["count"]})
        .pipe(lambda x: x.set_axis(x.columns.map("_".join), axis=1))
        .sort_values(by="mismatch_count", ascending=False)
    )
    logger.debug(grp)

    return data


def check_requirements():

    sql = "SELECT COUNT(*) FROM `{tablename}` LIMIT 1"
    ok = dbfuncs.query_fetchall(sql.format(tablename=envfuncs.get_var("ORDS_DATA")))
    if not ok:
        print("DATABASE ERROR: {}".format(envfuncs.get_var("ORDS_DATA")))
        print("TO FIX THIS EXECUTE: ords_db_mysql_setup.py")
    else:
        print("OK: table exists {}".format(envfuncs.get_var("ORDS_DATA")))

    ok = dbfuncs.query_fetchall(sql.format(tablename="ords_problem_translations"))
    if not ok:
        print("DATABASE ERROR: {}".format("ords_problem_translations"))
        print("TO FIX THIS EXECUTE: ords_deepl1_setup.py")
    else:
        print("OK: table exists {}".format("ords_problem_translations"))

    ok = deeplfuncs.check_api_key()
    if not ok:
        print("DEEPL ERROR: API KEY NOT FOUND")
        print("TO FIX THIS: add your DeepL API key to the .env file")
    else:
        print("OK: {}".format("DeepL API key found"))


def check_api_creds(mock=False):
    translator = deeplfuncs.deeplWrapper(mock)
    translator.api_limit_reached()


def do_deepl(mock=True, max=10, minlen=16, clause=1, lang=None):

    work = get_work(max, minlen, clause, lang)
    data = translate(work, mock)
    if not mock:
        insert_data(data)
        dbfuncs.dump_table_to_csv("ords_problem_translations", pathfuncs.DATA_DIR)
    else:
        logger.debug(data)
    exit()


def exec_opt(options):
    while True:
        for i, desc in options.items():
            print("{} : {}".format(i, desc))
        choice = input("Type a number: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice")
        else:
            if choice >= len(options):
                print("Out of range")
            else:
                f = options[choice]
                print(f)
                eval(f)


def get_options():
    # Check requirements first!
    # "mock=True" allows for trial and error without using up API credits.
    mock = False
    # Create a clause to implement a filter.
    # e.g. clause = 'country = "GBR"'
    # clause = "TRUE"
    clause = 'country = "GBR"'
    # Set a hard-coded language e.g. assuming all GBR recs are English.
    # else leave blank for language detection.
    lang = "en"
    print("Mock={}".format(mock))
    # Maximum no. of records to process, 10000 recommended for live run.
    max = 10000
    # Exclude records with problem text having characters less than this value.
    minlen = 16
    return {
        0: "exit()",
        1: "check_requirements()",
        2: "check_api_creds({})".format(mock),
        3: "do_deepl(mock={}, max={}, minlen={}, clause='{}', lang='{}')".format(
            mock, max, minlen, clause, lang
        ),
        4: "get_work(max={}, minlen={}, clause='{}', lang='{}')".format(
            max, minlen, clause, lang
        ),
    }


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    exec_opt(get_options())
