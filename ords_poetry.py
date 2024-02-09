#!/usr/bin/env python3

from funcs import *
import pandas as pd
import os
import json
from nltk import tokenize

# Challenge - build a Repair Haiku generator.
# https://spacy.io/universe/project/spacy_syllables


def write_poem(lang="en", lines=5, verses=12):
    df = pd.read_csv(pathfuncs.DATA_DIR + "/ords_poetry_lines.csv", dtype=str).dropna()
    df = df[df["language"].isin([lang])]
    for n in range(verses):
        rows = df.sample(lines)
        for i in range(0, len(rows)):
            print(rows.iloc[i].sentence)
            logger.debug(rows.iloc[i].sentence)
        print("")
        logger.debug("")


def test_poems():
    langs = get_langs()
    df = pd.read_csv(pathfuncs.DATA_DIR + "/ords_poetry_lines.csv", dtype=str).dropna()
    for key in langs.keys():
        print("*** {} ***".format(langs[key]))
        rows = df[df["language"].isin([key])].sample(3)
        for i in range(0, len(rows)):
            print(rows.iloc[i].sentence)
            logger.debug(rows.iloc[i].sentence)
        print("")
        logger.debug("")


# Split translations into sentences labelled with language.
def dump_data(minchars=2, maxchars=32):
    df_in = pd.read_csv(
        pathfuncs.DATA_DIR + "/ords_problem_translations.csv", dtype=str
    )
    logger.debug("Total translation records: {}".format(df_in.index.size))
    # Create output DataFrames, naming column `sentence` to remind that it is not the entire `problem` string.
    df_all = pd.DataFrame(columns=["sentence", "language"])
    langs = get_langs()
    for lang in langs.keys():
        logger.debug("*** LANGUAGE {} ***".format(lang))
        # Filter for non-empty unique strings in the `problem` column.
        df_tmp = clean_problem(
            pd.DataFrame(data=df_in[lang].unique(), columns=["problem"]).dropna()
        )
        print("Splitting sentences for lang {}".format(lang))
        for i, row in df_tmp.iterrows():
            if len(row.problem) > 0:
                try:
                    # Split the `problem` string into sentences.
                    sentences = tokenize.sent_tokenize(
                        row.problem, language=langs[lang]
                    )
                    df_tmp.at[i, "sentences"] = len(sentences)
                    # Add the sentences to the list for this language.
                    df_tmp.at[i, "sentence"] = sentences
                except Exception as error:
                    print(error)
        print("Appending sentences for lang {}".format(lang))
        # Expand the sentence list and save unique to DataFrame.
        df_lang = clean_sentence(df_tmp.explode("sentence"))
        # Reduce the results to comply with min/max sentence length.
        df_lang = df_lang[
            (
                df_lang["sentence"].apply(
                    lambda s: len(str(s)) in range(minchars, maxchars + 1)
                )
            )
        ]
        logger.debug(
            "Total usable sentences for lang {} : {}".format(lang, df_lang.index.size)
        )
        # Add the ISO lang code to the DataFrame for this language.
        df_lang["language"] = lang
        df_all = pd.concat([df_all, df_lang])

    df_all.to_csv(pathfuncs.DATA_DIR + "/ords_poetry_lines.csv", index=False)


def clean_problem(data, dedupe=True, dropna=True):
    # Make sure there is always a space after a period, else sentences won't be split.
    data.replace(
        {"problem": r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"},
        {"problem": "\\2. \\3"},
        regex=True,
        inplace=True,
    )
    # Remove HTML symbols (&gt; features a lot).
    data.replace(
        {"problem": r"(?i)(&[\w\s]+;)"}, {"problem": ""}, regex=True, inplace=True
    )
    # Trim whitespace from `problem` strings.
    data["problem"].str.strip()
    if dropna:
        # Drop `problem` values that may be empty after the replacements and trimming.
        data.dropna(subset=["problem"], inplace=True)
    if dedupe:
        # Dedupe the `problem` values.
        data.drop_duplicates(subset=["problem"], inplace=True)
    return data


def clean_sentence(data, dedupe=True, dropna=True):
    # Remove weight only values. (0.5kg, 5kg, 5 kg, .5kg etc.)
    data.replace(
        {"sentence": r"(?i)^(([0-9]+)?\.?[0-9\s]+kg\.?)$"},
        {"sentence": ""},
        regex=True,
        inplace=True,
    )
    # Remove numeric only values.
    data.replace(
        {"sentence": r"(?i)^(([0-9]+)?\.?[0-9\s]+\.?)$"},
        {"sentence": ""},
        regex=True,
        inplace=True,
    )
    # Remove short punctuation only values.
    data.replace(
        {"sentence": r"(?i)^([\d\W]{1,3}\.?)$"},
        {"sentence": ""},
        regex=True,
        inplace=True,
    )
    # Trim whitespace from `sentence` strings.
    data["problem"].str.strip()
    if dropna:
        # Drop `sentence` values that may be empty after the replacements and trimming.
        data.dropna(subset=["sentence"], inplace=True)
    if dedupe:
        # Dedupe the `sentence` values.
        data.drop_duplicates(subset=["sentence"], inplace=True)
    return data


# Split data into lists labelled with language.
def dump_json():
    df_in = pd.read_csv(pathfuncs.DATA_DIR + "/ords_poetry_lines.csv", dtype=str)
    langs = get_langs()
    dict = {}
    for lang in langs.keys():
        df_tmp = df_in[df_in["language"].isin([lang])]
        # df_tmp.sort_values(by)
        df_tmp.sort_values(by="sentence", key=lambda x: x.str.len(), inplace=True)
        dict[lang] = df_tmp["sentence"].tolist()

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
