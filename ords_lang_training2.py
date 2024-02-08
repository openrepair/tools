#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.model_selection import train_test_split
from joblib import dump
from joblib import load
from ords_lang_training import (
    exec_opt,
    format_path_out,
    clean_text,
    get_stopwords,
    get_alpha,
)

# THIS VERSION DOES NOT SPLIT THE PROBLEM TEXT.
# MORE USEFUL FOR VALIDATION.


# For each entire problem text string.
# Clean, dropna and dedupe.
# Sample for training and validation.
def dump_data(sample=0.3, minchars=12, maxchars=65535):
    # Read input DataFrame.
    df_in = pd.read_csv(
        pathfuncs.DATA_DIR + "/ords_problem_translations.csv", dtype=str
    ).query('language_known != "??"')

    df_in = pd.DataFrame(data=df_in[["language_known", "country", "problem"]])
    df_in.rename({"language_known": "language"}, axis=1, inplace=True)
    df_in["problem_orig"] = df_in["problem"]
    logger.debug("Total translation records: {}".format(df_in.index.size))
    df_in = clean_text(df_in)
    df_in["problem"].apply(lambda s: len(str(s)) in range(minchars, maxchars + 1))
    df_in.dropna(inplace=True, axis=0)

    # Take % of the data for validation.
    df_train, df_valid = train_test_split(df_in, test_size=sample)
    logger.debug(
        "Validation data: {} ({})".format(
            df_valid.index.size,
            df_valid.index.size / df_in.index.size,
        )
    )
    logger.debug(
        "Training data: {} ({})".format(
            df_train.index.size,
            df_train.index.size / df_in.index.size,
        )
    )

    logger.debug("*** ALL USEABLE DATA ***")
    logger.debug(df_in.index.size)

    logger.debug("*** TRAINING DATA ***")
    logger.debug(df_train.index.size)
    logger.debug(df_train.index.size / df_in.index.size)

    logger.debug("*** VALIDATION DATA ***")
    logger.debug(df_valid.index.size)
    logger.debug(df_valid.index.size / df_in.index.size)

    # Save the data to the 'out' directory in csv format for use later.
    df_train.to_csv(format_path_out("ords_lang_data_training2"), index=False)
    df_valid.to_csv(format_path_out("ords_lang_data_validation2"), index=False)


def do_training():
    data = pd.read_csv(format_path_out("ords_lang_data_training2"), dtype=str).dropna()

    column = data.problem
    labels = data.language

    vectorizer = TfidfVectorizer()
    vectorizer.set_params(stop_words=get_stopwords())

    classifier = MultinomialNB(force_alpha=True, alpha=0.1)

    pipe = Pipeline(
        [
            ("tfidf", vectorizer),
            ("clf", classifier),
        ]
    )
    pipe.fit(column, labels)
    dump(pipe, get_pipefile())
    predictions = pipe.predict(column)
    score = metrics.f1_score(labels, predictions, average="macro")
    logger.debug("** TRAIN : F1 SCORE: {}".format(score))

    # Save predictions to 'out' directory in csv format.
    data.loc[:, "prediction"] = predictions
    data.to_csv(format_path_out("ords_lang_results_training2"), index=False)

    # Save prediction misses.
    misses = data[(data["language"] != data["prediction"])]
    misses.to_csv(format_path_out("ords_lang_misses_training2"), index=False)


def do_validation(pipeline=True):
    data = pd.read_csv(
        format_path_out("ords_lang_data_validation2"), dtype=str
    ).dropna()
    column = data.problem
    labels = data.language
    logger.debug("** VALIDATE : using pipeline - {}".format(pipeline))
    if pipeline:
        # Use the pipeline that was fitted for this task.
        pipe = load(get_pipefile())
        predictions = pipe.predict(data.problem)
    else:
        # Use the classifier and vectoriser that were fitted for this task.
        classifier = load(get_clsfile())
        vectorizer = load(get_tdffile())
        feature_vects = vectorizer.transform(column)
        predictions = classifier.predict(feature_vects)

    score = metrics.f1_score(labels, predictions, average="macro")
    logger.debug("** VALIDATE : F1 SCORE: {}".format(score))
    logger.debug(metrics.classification_report(labels, predictions))

    # Predictions output for inspection.
    data.loc[:, "prediction"] = predictions
    data.to_csv(format_path_out("ords_lang_results_validation2"), index=False)

    # Prediction misses for inspection.
    misses = data[(data.language != data["prediction"])]
    misses.to_csv(format_path_out("ords_lang_misses_validation2"), index=False)


# Use model on untrained data, with either pipeline or vect/class objects.
def do_detection(pipeline=True):
    data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
    data.dropna(axis="rows", subset=["problem"], inplace=True, ignore_index=True)
    column = data.problem
    logger.debug("** DETECT : using pipeline - {}".format(pipeline))
    if pipeline:
        # Use the pipeline that was fitted for this task.
        pipe = load(get_pipefile())
        predictions = pipe.predict(data.problem)
    else:
        # Use the classifier and vectoriser that were fitted for this task.
        classifier = load(get_clsfile())
        vectorizer = load(get_tdffile())
        feature_vects = vectorizer.transform(column)
        predictions = classifier.predict(feature_vects)

    # Predictions output.
    data.loc[:, "prediction"] = predictions
    data = data.reindex(columns=["id", "problem", "prediction"])
    data.to_csv(format_path_out("ords_lang_results_detection2"), index=False)
    return data


# Find records that were missed by the validator.
# Can uncover issues with the source translation.
def misses_report(type):
    logger.debug("misses_report: {}".format(type))
    df_in = pd.read_csv(
        pathfuncs.OUT_DIR + "/ords_lang_misses_{}2.csv".format(type),
        dtype=str,
        keep_default_na=False,
        na_values="",
    )
    results = []
    for i, row in df_in.iterrows():
        sql = """
        SELECT
        id_ords,
        country,
        language_known,
        '{0}' as language_trans,
        '{1}' as prediction,
        `{0}` as `text`,
        problem
        FROM `ords_problem_translations`
        WHERE `problem` = %(problem)s
        ORDER BY id_ords
        """
        db_res = dbfuncs.query_fetchall(
            sql.format(row["language"], row["prediction"]),
            {"problem": row["problem_orig"]},
        )
        if (not db_res) or len(db_res) == 0:
            logger.debug("NOT FOUND: {}".format(row["problem_orig"]))
        else:
            results.extend(db_res)

    df_out = pd.DataFrame(data=results).sort_values(by=["id_ords"])
    df_out.to_csv(
        pathfuncs.OUT_DIR + "/ords_lang_misses_{}2_ids.csv".format(type), index=False
    )
    logger.debug("misses: {}".format(len(df_out.index)))


# Check char by char using differ.
def charcheck():
    import difflib

    d = difflib.Differ()

    langs = {
        "en": "english",
        "de": "german",
        "nl": "dutch",
        "fr": "french",
        "it": "italian",
        "es": "spanish",
        "da": "danish",
    }

    sql = """SELECT `id_ords`, `language_known`,
1 as what,
'' as diff,
`problem`,
`{0}` as trans
FROM `ords_problem_translations`
WHERE `language_known` = '{0}'
AND(
LENGTH(`{0}`) <> LENGTH(`problem`)
OR REGEXP_REPLACE(LOWER(`{0}`), ' ', '') <> REGEXP_REPLACE(LOWER(`problem`), ' ', '')
)
"""

    df = pd.DataFrame()
    for lang in langs.keys():
        df_res = pd.DataFrame(dbfuncs.query_fetchall(sql.format(lang)))
        df = pd.concat([df, df_res])

    df.reset_index(inplace=True)
    for i, row in df.iterrows():
        p = row.problem
        t = row.trans
        diff = list(set([s for s in list(d.compare(p, t)) if s[0] in ["-", "+"]]))
        df.at[i, "diff"] = ",".join(diff)
        if (len(diff) == 1) & (diff[0].strip() == "-"):
            df.at[i, "what"] = 0

    df.sort_values(by=["what", "problem"], inplace=True, ignore_index=True)
    df.to_csv(pathfuncs.OUT_DIR + "/ords_lang_training2_charcheck.csv", index=False)

    exit()


def get_pipefile():
    return format_path_out("ords_lang_obj2_tfidf_cls", "joblib")


def get_clsfile():
    return format_path_out("ords_lang_obj2_cls", "joblib")


def get_tdffile():
    return format_path_out("ords_lang_obj2_tdif", "joblib")


def get_options():
    return {
        0: "exit()",
        1: "dump_data(sample=0.3, minchars=12, maxchars=65535)",
        2: "do_training()",
        3: "misses_report('training')",
        4: "do_validation()",
        5: "misses_report('validation')",
        6: "do_detection()",
        7: "charcheck()",
    }


if __name__ == "__main__":
    logger = logfuncs.init_logger(__file__)
    exec_opt(get_options())
