#!/usr/bin/env python3

# Challenge - build a Repair Haiku generator.
# https://spacy.io/universe/project/spacy_syllables

import polars as pl
import json
from nltk import tokenize
from funcs import *


def write_poem(lang="en", lines=5, verses=12):
    df = pl.read_csv(cfg.DATA_DIR + "/ords_poetry_lines.csv")
    df = df.filter(
        pl.col("language") == pl.lit(lang),
    )
    for n in range(verses):
        rows = df.sample(lines)
        for sent, lang in rows.iter_rows():
            print(sent)
            logger.debug(sent)
        print("")
        logger.debug("")


def test_poems():
    langs = get_langs()
    df = pl.read_csv(cfg.DATA_DIR + "/ords_poetry_lines.csv")
    for key in langs.keys():
        logger.debug(f"*** {langs[key]} ***")
        print(f"*** {langs[key]} ***")
        rows = df.filter(
            pl.col("language") == pl.lit(key),
        ).sample(3)
        for sent, lang in rows.iter_rows():
            print(sent)
            logger.debug(sent)
        print("")
        logger.debug("")


# Split translations into sentences labelled with language.
def dump_data(minchars=2, maxchars=32):
    df_in = pl.read_csv(cfg.DATA_DIR + "/ords_problem_translations.csv")
    logger.debug(f"Total translation records: {len(df_in)}")
    # Create output DataFrames, naming column `sentence` to remind that it is not the entire `problem` string.
    df_all = pl.DataFrame(
        schema={"sentence": pl.String, "language": pl.String}, orient="col"
    )
    langs = get_langs()
    for lang in langs.keys():
        logger.debug(f"*** LANGUAGE {lang} ***")
        # Filter for non-empty unique strings in the `problem` column.
        data = (
            df_in.unique(subset=[lang], maintain_order=True)
            .drop_nulls()
            .select(
                pl.col(
                    "id_ords",
                    lang,
                )
            )
            .rename({lang: "problem"})
            .with_columns(sentences=pl.lit(0))
        )

        df_tmp = textfuncs.clean_text(data, "problem")
        logger.debug(f"Total problems for lang {lang} : {df_tmp.height}")
        print(f"Splitting sentences for lang {lang}")
        sentlist = []
        for row in df_tmp.iter_rows(named=True):
            if len(row["problem"]) > 0:
                try:
                    # Split the `problem` string into sentences.
                    stoks = tokenize.sent_tokenize(row["problem"], language=langs[lang])
                    sentlist.extend(stoks)
                    df_tmp = df_tmp.with_columns(
                        sentences=pl.when(pl.col("id_ords") == row["id_ords"])
                        .then(len(stoks))
                        .otherwise(pl.col("sentences")),
                    )
                except Exception as error:
                    print(error)

        logger.debug(f"Total parsed rows for lang {lang} : {df_tmp.height}")
        print(f"Appending sentences for lang {lang}")
        df_lang = pl.DataFrame(
            schema={"sentence": pl.String}, orient="col", data=[sentlist]
        )

        df_lang = textfuncs.clean_text(df_lang, "sentence").with_columns(
            pl.col("sentence").str.strip_chars(".").str.strip_chars()
        )
        logger.debug(f"Total cleaned sentences for lang {lang} : {df_lang.height}")
        # Reduce the results to comply with min/max sentence length.
        df_lang = (
            df_lang.filter(
                pl.col("sentence").str.len_chars().is_between(minchars, maxchars + 1),
            )
            .select(
                pl.col(
                    "sentence",
                )
            )
            .with_columns(
                language=pl.lit(lang),
            )
        )
        logger.debug(f"Total usable sentences for lang {lang} : {df_lang.height}")
        df_all = pl.concat([df_all, df_lang])

    df_all.write_csv(cfg.DATA_DIR + "/ords_poetry_lines.csv")


# Split data into lists labelled with language.
def dump_json():
    df_in = pl.read_csv(cfg.DATA_DIR + "/ords_poetry_lines.csv")
    langs = get_langs()
    dict = {}
    for lang in langs.keys():

        df_tmp = df_in.filter(
            pl.col("language") == pl.lit(lang),
        )
        df_tmp = df_tmp.sort(pl.col("sentence").str.len_chars())
        dict[lang] = list(df_tmp["sentence"])

    file = "poetry/data"
    with open(file + ".json", "w") as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)

    with open(file + ".js", "w") as f:
        f.write("data=" + json.dumps(dict, indent=4, ensure_ascii=False))


# Map ISO lang codes to the names of the nltk language models.
def get_langs():
    return {
        "en": "english",
        "de": "german",
        "nl": "dutch",
        "fr": "french",
        "it": "italian",
        "es": "spanish",
        "da": "danish",
    }


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    while True:
        eval(
            miscfuncs.exec_opt(
                ["dump_data()", "dump_json()", "test_poems()", "write_poem()"]
            )
        )
