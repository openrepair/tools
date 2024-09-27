#!/usr/bin/env python3

import polars as pl
from funcs import cfg
from funcs import ordsfuncs as of


def check_languages(df_trans, langs):

    # Language detection stats.
    logger.debug("*** DETECTED ***")
    df = df_trans.group_by(["language_detected"]).len().sort("len", descending=True)
    # Known languages detected.
    logger.debug("*** KNOWN LANGUAGES DETECTED***")
    df_known = df.filter(pl.col("language_detected").is_in(langs))
    logger.debug(df_known)
    # Unknown languages detected.
    logger.debug("*** UNKNOWN LANGUAGE DETECTED***")
    df_unknown = df.filter(pl.col("language_detected").is_in(langs).not_())
    logger.debug(df_unknown)

    # Detected language does not match "known" language.
    # Note that "known" language could be incorrect.
    # Log summary and write to csv file.
    logger.debug("*** MISMATCHED LANGUAGE DETECTION ***")
    path = f"{cfg.OUT_DIR}/deepl_misdetect.csv"
    logger.debug("See " + path)

    df = (
        df_trans.group_by(["language_known", "language_detected"])
        .len()
        .sort("len", descending=True)
        .filter(pl.col("language_detected") != pl.col("language_known"))
    )
    logger.debug(df)

    df = (
        df_trans.filter(pl.col("language_detected") != pl.col("language_known"))
        .select(["id_ords", "language_known", "language_detected", "problem"])
        .sort(by=["language_detected", "language_known"])
    )
    df.write_csv(path)


def check_translations(df_trans, langs):

    # Identical translations across languages.
    # Could be bad language detected or malformed problem text.
    # Write results to csv file.
    logger.debug("*** IDENTICAL TRANSLATIONS ***")
    path = f"{cfg.OUT_DIR}/deepl_mistranslate.csv"
    logger.debug("See " + path)
    df = df_trans.filter(
        (pl.col("en") == pl.col("problem"))
        & (pl.col("de") == pl.col("problem"))
        & (pl.col("nl") == pl.col("problem"))
        & (pl.col("fr") == pl.col("problem"))
        & (pl.col("it") == pl.col("problem"))
        & (pl.col("es") == pl.col("problem"))
        & (pl.col("da") == pl.col("problem"))
    ).sort(by=["language_detected", "language_known"])
    df.write_csv(path)

    # Translation gaps.
    # Could have run out of DeepL credits before lang set completion.
    logger.debug("*** MISSING TRANSLATIONS ***")
    path = f"{cfg.OUT_DIR}/deepl_missing.csv"
    logger.debug("See " + path)
    df = df_trans.select(langs).null_count()
    logger.debug(df)
    for col in langs:
        df_null = df_trans.filter(pl.col(col).is_null()).select(
            ["id_ords", "language_known", "problem", col]
        )
        if df_null.height > 0:
            logger.debug(df_null)


def check_status(df_trans):

    logger.debug("*** STATUS ***")
    path = f"{cfg.OUT_DIR}/deepl_status.csv"
    logger.debug("See " + path)
    df_ords = of.get_data("OpenRepairData_v0.3_aggregate_202407").drop_nulls(
        subset="problem"
    )
    df = (
        df_ords.filter((pl.col("problem").str.len_chars() >= 16))
        .join(df_trans, left_on="id", right_on="id_ords", how="anti")
        .group_by(["problem"])
        .len()
        .sort("len", descending=True)
    )
    df.write_csv(path)


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    langs = ["en", "de", "nl", "fr", "it", "es", "da"]
    df_trans = pl.read_csv(f"{cfg.DATA_DIR}/ords_problem_translations.csv")

    check_languages(df_trans, langs)
    check_translations(df_trans, langs)
    check_status(df_trans)
