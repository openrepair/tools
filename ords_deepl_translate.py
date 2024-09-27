#!/usr/bin/env python3

import polars as pl
import deepl
from funcs import *


"""
To Do:

1. Exclude duplicate problem text.
2. Handle short/useless problem text.

"""


def get_work(minlen=64, maxlen=512, maxrows=1):

    logger.debug("*** get_work ***")

    df_trans = pl.read_csv(f"{cfg.DATA_DIR}/ords_problem_translations.csv").select(
        "id_ords"
    )
    df_ords = (
        ordsfuncs.get_data("OpenRepairData_v0.3_aggregate_202407")
        .drop_nulls(subset="problem")
        .rename({"id": "id_ords"})
        .select(["id_ords", "data_provider", "country", "problem"])
    )

    df = pl.DataFrame()
    countries = [
        {"country": "DEU", "providers": ["anstiftung"], "lang": "de"},
        {"country": "BEL", "providers": ["The Restart Project"], "lang": "fr"},
        {"country": "GBR", "providers": ["The Restart Project"], "lang": "en"},
    ]
    for elem in countries:
        country = elem["country"]
        providers = elem["providers"]
        df_tmp = df_ords.filter(
            (pl.col("problem").str.len_chars().is_between(minlen,maxlen))
            & (pl.col("country") == country)
        )
        if providers != None:
            df_tmp = df_tmp.filter(
                pl.col("data_provider").is_in(providers)
            ).with_columns(language_known=pl.lit(elem["lang"]))
        df_tmp = df_tmp.join(df_trans, on="id_ords", how="anti")
        df_tmp.write_csv(f"{cfg.OUT_DIR}deepl_work_{country}_{minlen}.csv")
        df = pl.concat([df, df_tmp])

    df = df.unique(subset="id_ords").limit(maxrows)
    logger.debug(df)
    df.write_csv(f"{cfg.OUT_DIR}deepl_work.csv")
    print(f"Work written to {cfg.OUT_DIR}deepl_work.csv")
    return df


def translate(mock=True, max=1):

    logger.debug("*** translate ***")

    work = pl.read_csv(f"{cfg.OUT_DIR}deepl_work.csv")
    translator = deeplfuncs.deeplWrapper(mock)
    langdict = deeplfuncs.deeplWrapper.langdict
    data = pl.DataFrame()
    schema_trans = {
        "id_ords": pl.String,
        "data_provider": pl.String,
        "country": pl.String,
        "problem": pl.String,
        "language_known": pl.String,
    }
    try:
        # For each record fetch a translation for each target language.
        i = 0
        t = work.height
        for row in work.iter_rows(named=True):
            df_tmp = pl.DataFrame(data=row, schema=schema_trans).with_columns(
                pl.lit("DeepL").alias("translator"),
                pl.lit("").alias("language_detected"),
            )
            i += 1
            lang_k = row["language_known"]
            lang_d = ""
            print(f"{i}/{t} : {row['id_ords']}")
            for column in langdict.keys():
                # Get the target language.
                lang_t = langdict[column]
                # Is the target language the same as the known language?
                if column == lang_k:
                    # Don't use up API credits.
                    text = row["problem"]
                else:
                    try:
                        result = translator.translate_text(
                            row["problem"], target_lang=lang_t, source_lang=lang_k
                        )
                        lang_d = result.detected_source_lang.lower()
                        text = result.text
                    except deepl.DeepLException as error:
                        print(f"Exception: {error}")
                        logger.debug(error)
                        logger.debug(df_tmp)
                        break

                df_tmp = df_tmp.with_columns(
                    translator=pl.lit("DeepL"),
                    language_detected=pl.lit(lang_d),
                ).with_columns(pl.lit(text).alias(column))

            data = pl.concat([data, df_tmp])

    except Exception as error:
        print(f"Exception: {error}")

    finally:
        write_latest(data)
        return data


def write_latest(data):
    logger.debug(data.columns)
    logger.debug(data)
    data.write_csv(f"{cfg.OUT_DIR}deepl_latest.csv")
    print(f"Translations written to {cfg.OUT_DIR}deepl_latest.csv")


def write_translations(mock):

    logger.debug("*** write_translations ***")
    try:
        df_new = pl.read_csv(f"{cfg.OUT_DIR}deepl_latest.csv")
        df_trans = pl.read_csv(f"{cfg.DATA_DIR}ords_problem_translations.csv")
        df = pl.concat([df_trans, df_new]).unique(subset="id_ords")
        out = cfg.DATA_DIR
        file = "ords_problem_translations"
        if mock:
            out = cfg.OUT_DIR
            file = f"{file}_mock"
        df.write_csv(f"{out}{file}.csv")
        print(f"Translations written to {out}{file}")
        df_new.write_csv(f"{cfg.OUT_DIR}deepl_latest_appended.csv")
        pathfuncs.rm_file(f"{cfg.OUT_DIR}deepl_latest.csv")
    except Exception as error:
        print(f"Exception: {error}")


def check_requirements():

    ok = deeplfuncs.check_api_key()
    if not ok:
        print("DEEPL ERROR: API KEY NOT FOUND")
        print("TO FIX THIS: add a DeepL API key to the .env file")
    else:
        print("DeepL API key found")

    files = [
        f"{cfg.DATA_DIR}ords_problem_translations.csv",
        f"{cfg.DATA_DIR}ords/OpenRepairData_v0.3_aggregate_202407.csv",
        f"{cfg.OUT_DIR}deepl_work.csv",
        f"{cfg.OUT_DIR}deepl_latest.csv",
    ]

    try:
        for file in files:
            if not pathfuncs.check_path(file):
                print(f"{file} NOT found")
                continue
            print(f"{file} found")
    except Exception as error:
        print(f"Exception: {error}")


def check_api_creds(mock=False):
    translator = deeplfuncs.deeplWrapper(mock)
    translator.api_limit_reached()


def do_pipeline(minlen, maxrows, mock):

    get_work(minlen, maxrows)
    translate(mock)
    write_translations(mock)
    exit()


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    # "mock=True" allows for trial and error without using up API credits.
    mock = False
    minlen = 64
    maxlen = 128
    maxrows = 1000

    while True:
        eval(
            miscfuncs.exec_opt(
                [
                    f"check_requirements()",
                    f"check_api_creds({mock})",
                    f"get_work(minlen={minlen}, maxrows={maxrows})",
                    f"translate(mock={mock})",
                    f"write_translations(mock={mock})",
                    f"do_pipeline(minlen={minlen}, maxlen={maxlen}, maxrows={maxrows}, mock={mock})",
                ]
            )
        )
