#!/usr/bin/env python3

# Challenge - build a Repair Haiku generator.
# https://spacy.io/universe/project/spacy_syllables

import polars as pl
import json
from nltk import tokenize
from funcs import *


def write_poem(lang="en", lines=5, verses=12):
    df = pl.read_csv(ordsfuncs.DATA_DIR + "/ords_poetry_lines.csv")
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
    df = pl.read_csv(ordsfuncs.DATA_DIR + "/ords_poetry_lines.csv")
    for key in langs.keys():
        logger.debug("*** {} ***".format(langs[key]))
        print("*** {} ***".format(langs[key]))
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
    df_in = pl.read_csv(ordsfuncs.DATA_DIR + "/ords_problem_translations.csv")
    logger.debug("Total translation records: {}".format(len(df_in)))
    # Create output DataFrames, naming column `sentence` to remind that it is not the entire `problem` string.
    df_all = pl.DataFrame(
        schema={"sentence": pl.String, "language": pl.String}, orient="col"
    )
    langs = get_langs()
    for lang in langs.keys():
        logger.debug("*** LANGUAGE {} ***".format(lang))
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
        df_tmp = clean_problem(data)
        logger.debug("Total problems for lang {} : {}".format(lang, df_tmp.height))
        print("Splitting sentences for lang {}".format(lang))
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

        logger.debug("Total parsed rows for lang {} : {}".format(lang, df_tmp.height))
        print("Appending sentences for lang {}".format(lang))
        df_lang = pl.DataFrame(
            schema={"sentence": pl.String}, orient="col", data=[sentlist]
        )
        df_lang = clean_sentence(df_lang)
        logger.debug(
            "Total cleaned sentences for lang {} : {}".format(lang, df_lang.height)
        )
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
        logger.debug(
            "Total usable sentences for lang {} : {}".format(lang, df_lang.height)
        )
        df_all = pl.concat([df_all, df_lang])

    df_all.write_csv(ordsfuncs.DATA_DIR + "/ords_poetry_lines.csv")


def clean_problem(data, dedupe=True, dropna=True):
    # 1.
    p = r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"
    s = "${2}. ${3}"
    data = data.with_columns(pl.col("problem").str.replace(p, s))

    # 2.
    p = r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"
    s = "\\2. \\3"
    data = data.with_columns(pl.col("problem").str.replace(p, s))

    # 3.Remove HTML symbols (&gt; features a lot).
    p = r"(?i)(&[\w\s]+;)"
    s = ""
    data = data.with_columns(pl.col("problem").str.replace(p, s))

    # Trim whitespace from `problem` strings.
    data = data.with_columns(pl.col("problem").str.strip_chars())
    if dropna:
        # Drop `problem` values that may be empty after the replacements and trimming.
        data = data.drop_nulls(subset=["problem"])
    if dedupe:
        # Dedupe the `problem` values.
        data = data.unique(subset=["problem"], maintain_order=True)
    return data


def clean_sentence(data, dedupe=True, dropna=True):
    # Remove weight only values. (0.5kg, 5kg, 5 kg0
    # , .5kg etc.)
    p = r"(?i)^(([0-9]+)?\.?[0-9\s]+kg\.?)$"
    s = ""
    data = data.with_columns(pl.col("sentence").str.replace(p, s))

    # Remove numeric only values.
    p = r"(?i)^(([0-9]+)?\.?[0-9\s]+\.?)$"
    s = ""
    data = data.with_columns(pl.col("sentence").str.replace(p, s))

    # Remove short punctuation only values.
    p = r"(?i)^([\d\W]{1,3}\.?)$"
    s = ""
    data = data.with_columns(pl.col("sentence").str.replace(p, s))

    # Trim whitespace and periods from `sentence` strings.
    data = data.with_columns(pl.col("sentence").str.strip_chars().str.strip_chars(".").str.strip_chars())

    if dropna:
        # Drop `sentence` values that may be empty after the replacements and trimming.
        data = data.drop_nulls(subset=["sentence"])
    if dedupe:
        # Dedupe the `sentence` values.
        data = data.unique(subset=["sentence"], maintain_order=True)

    return data


# Split data into lists labelled with language.
def dump_json():
    df_in = pl.read_csv(ordsfuncs.DATA_DIR + "/ords_poetry_lines.csv")
    langs = get_langs()
    dict = {}
    for lang in langs.keys():

        df_tmp = df_in.filter(
            pl.col("language") == pl.lit(lang),
        )
        df_tmp = df_tmp.sort(pl.col("sentence").str.len_chars())
        dict[lang] = list(df_tmp["sentence"])

    file = "poetry/data.json"
    with open(file, "w") as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)


# Select function to run.
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
    return {
        0: "exit()",
        1: "dump_data()",
        2: "dump_json()",
        3: "test_poems()",
        4: "write_poem()",
    }


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

    logger = logfuncs.init_logger(__file__)

    exec_opt(get_options())
