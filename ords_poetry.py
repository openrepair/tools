#!/usr/bin/env python3

from funcs import *
import pandas as pd
import os
from nltk import tokenize

logger = logfuncs.init_logger(__file__)

# Challenge - build a Repair Haiku generator.
# https://spacy.io/universe/project/spacy_syllables


def gen(lang="en", lines=5, verses=12):
    df = pd.read_csv(pathfuncs.DATA_DIR + "/ords_poetry_lines.csv", dtype=str).dropna()
    df = df[df["language"].isin([lang])]
    os.system("clear")
    for n in range(verses):
        rows = df.sample(n=lines)
        for i in range(0, len(rows)):
            print(rows.iloc[i].sentence)
            logger.debug(rows.iloc[i].sentence)
        print("")
        logger.debug("")


# Split translations into sentences labelled with language.
def dump_data(minchars=1, maxchars=32):
    df_in = pd.read_csv(
        pathfuncs.DATA_DIR + "/ords_problem_translations.csv", dtype=str
    )
    logger.debug("Total translation records: {}".format(df_in.index.size))
    # Create output DataFrames, naming column `sentence` to remind that it is not the entire `problem` string.
    df_all = pd.DataFrame(columns=["problem", "sentence", "language"])
    for lang in langs.keys():
        logger.debug("*** LANGUAGE {} ***".format(lang))
        # Filter for non-empty unique strings in the `problem` column.
        df_tmp = clean_text(
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
        df_lang = df_tmp.explode("sentence").drop_duplicates()
        # Trim whitespace from `sentence` strings (again).
        df_lang["sentence"].str.strip()
        # Add the ISO lang code to the DataFrame for this language.
        df_lang["language"] = lang
        logger.debug(
            "Total sentences for lang {} : {}".format(lang, df_lang.index.size)
        )
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
        df_all = pd.concat([df_all, df_lang])

    df_all.to_csv(pathfuncs.DATA_DIR + "/ords_poetry_lines.csv", index=False)


def clean_text(data, dedupe=True, dropna=True):
    # Make sure there is always a space after a period, else sentences won't be split.
    data.replace(
        {"problem": r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"},
        {"problem": "\\2. \\3"},
        regex=True,
        inplace=True,
    )
    # Remove HTML symbols (&gt; features a lot)
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


# Get language choice.
def exec_opt(options):
    for i, desc in options.items():
        print("{} : {}".format(i, desc))
    choice = input("Choose a language (or 0 to quit): ")
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice")
    else:
        if choice == 0:
            exit()
        if choice >= len(options):
            print("Out of range")
        else:
            lang = options[choice]
            key = [key for key, val in langs.items() if val == lang.lower()]
            if len(key) == 1:
                gen(key[0])
            else:
                print("Key not found: {}".format(lang))


# Map ISO lang codes to the names of the nltk language models.
langs = {
    "en": "english",
    "de": "german",
    "nl": "dutch",
    "fr": "french",
    "it": "italian",
    "es": "spanish",
    "da": "danish",
}

# Should new translations be available.
# dump_data()
# exit()

# Use the langs dict to create the choices.
options = pd.Series(data=langs.values(), index=list(range(1, 8)))
# Run command line interaction.
exec_opt(options.str.capitalize())
