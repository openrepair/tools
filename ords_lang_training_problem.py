#!/usr/bin/env python3

# THIS VERSION DOES NOT SPLIT THE PROBLEM TEXT FOR TRAINING.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn import model_selection
from sklearn.model_selection import train_test_split
from joblib import dump
from joblib import load
import polars as pl
from funcs import *


def format_path_out(filename, ext="csv", suffix=""):
    return f"{cfg.OUT_DIR}/{filename}_{suffix}.{ext}"


# Use this to check for best value and set it as default
# Don't use every time, it slows down execution considerably.
def get_alpha(data, labels, vects, search=False):
    if search:
        # Try out some alpha values to find the best one for this data.
        params = {
            "alpha": [0, 0.001, 0.01, 0.1, 5, 10],
        }
        # Instantiate the search with the model we want to try and fit it on the training data.
        cvval = 12
        if len(data) < cvval:
            cvval = len(data)
        multinomial_nb_grid = model_selection.GridSearchCV(
            MultinomialNB(),
            param_grid=params,
            scoring="f1_macro",
            n_jobs=-1,
            cv=cvval,
            refit=False,
            verbose=2,
        )
        multinomial_nb_grid.fit(vects, labels)
        msg = f"** TRAIN: classifier best alpha value(s): {multinomial_nb_grid.best_params_}"
        logger.debug(msg)
        print(msg)
        return multinomial_nb_grid.best_params_["alpha"]
    else:
        return 0.1


# In the case of repair data, ignore acronyms and jargon.
def get_stopwords():
    stopfile = open(f"{cfg.DATA_DIR}/ords_lang_training_stopwords.txt", "r")
    stoplist = list(stopfile.read().replace("\n", " "))
    stopfile.close()
    return stoplist


# For each entire problem text string.
# Clean, drop nulls and dedupe.
# Sample for training and validation.
def dump_data(sample=0.3, minchars=12, maxchars=65535):

    # Read input DataFrame.
    df_in = (
        pl.read_csv(f"{cfg.DATA_DIR}/ords_problem_translations.csv")
        .filter(pl.col("language_known") != pl.lit("??"))
        .select("language_known", "country", "problem")
        .rename({"language_known": "language"})
        .with_columns(problem_orig=pl.col("problem"))
    )

    logger.debug(f"Total translation records: {df_in.height}")

    df_in = textfuncs.clean_text(df_in, "problem").filter(
        pl.col("problem").str.len_chars().is_between(minchars, maxchars + 1)
    )

    # Take % of the data for validation.
    df_train, df_valid = train_test_split(df_in, test_size=sample)

    logger.debug("*** ALL USEABLE DATA ***")
    logger.debug(df_train.height + df_valid.height)

    logger.debug("*** TRAINING DATA ***")
    logger.debug(df_train.height)
    logger.debug(df_train.height / (df_train.height + df_valid.height))

    logger.debug("*** VALIDATION DATA ***")
    logger.debug(df_valid.height)
    logger.debug(df_valid.height / (df_train.height + df_valid.height))

    # Save the data to the 'out' directory in csv format for use later.
    df_train.write_csv(format_path_out("ords_lang_data_training", "csv", file_suffix))
    df_valid.write_csv(format_path_out("ords_lang_data_validation", "csv", file_suffix))


def do_training():

    data = pl.read_csv(format_path_out("ords_lang_data_training", "csv", file_suffix))
    column = data["problem"]
    labels = data["language"]

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
    logger.debug(f"** TRAIN : F1 SCORE: {score}")

    # Save predictions to 'out' directory in csv format.
    data = data.with_columns(prediction=predictions)
    data.write_csv(format_path_out("ords_lang_results_training", "csv", file_suffix))

    # Save prediction misses.
    misses = data.filter(pl.col("language") != pl.col("prediction"))
    misses.write_csv(format_path_out("ords_lang_misses_training", "csv", file_suffix))


def do_validation(pipeline=True):

    data = pl.read_csv(format_path_out("ords_lang_data_validation", "csv", file_suffix))
    column = data["problem"]
    labels = data["language"]

    logger.debug(f"** VALIDATE : using pipeline - {pipeline}")
    if pipeline:
        # Use the pipeline that was fitted for this task.
        pipe = load(get_pipefile())
        predictions = pipe.predict(column)
    else:
        # Use the classifier and vectoriser that were fitted for this task.
        classifier = load(get_clsfile())
        vectorizer = load(get_tdffile())
        feature_vects = vectorizer.transform(column)
        predictions = classifier.predict(feature_vects)

    score = metrics.f1_score(labels, predictions, average="macro")
    logger.debug(f"** VALIDATE : F1 SCORE: {score}")
    logger.debug(metrics.classification_report(labels, predictions))

    # Predictions output for inspection.
    data = data.with_columns(prediction=predictions)
    data.write_csv(format_path_out("ords_lang_results_validation", "csv", file_suffix))

    # Prediction misses for inspection.
    misses = data.filter(pl.col("language") != pl.col("prediction"))
    misses.write_csv(format_path_out("ords_lang_misses_validation", "csv", file_suffix))


# Use model on untrained data, with either pipeline or vect/class objects.
def do_detection(pipeline=True):

    data = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")).drop_nulls(subset="problem")
    column = data["problem"]

    logger.debug(f"** DETECT : using pipeline - {pipeline}")
    if pipeline:
        # Use the pipeline that was fitted for this task.
        pipe = load(get_pipefile())
        predictions = pipe.predict(column)
    else:
        # Use the classifier and vectoriser that were fitted for this task.
        classifier = load(get_clsfile())
        vectorizer = load(get_tdffile())
        feature_vects = vectorizer.transform(column)
        predictions = classifier.predict(feature_vects)

    # Predictions output.
    data = data.with_columns(prediction=predictions)
    data.write_csv(format_path_out("ords_lang_results_detection", "csv"))


# Can uncover translations where original text no longer exists or has changed.
# Requires database with latest translations.
# To Do: refactor for dataframe.
def missing_problem_text(type):

    dbfuncs.dbvars = cfg.get_dbvars()

    logger.debug(f"misses_report: {type}")
    # problem_orig,problem,sentence,language,country,prediction
    df_in = pl.read_csv(format_path_out(f"ords_lang_misses_{type}", "csv", file_suffix))
    cols = df_in.columns
    language = cols.index("language")
    problem = cols.index("problem")
    problem_orig = cols.index("problem_orig")
    prediction = cols.index("prediction")
    results = []
    for row in df_in.iter_rows():
        sql = f"""SELECT
id_ords,
country,
language_known,
'{row[language]}' as language_trans,
'{row[prediction]}' as prediction,
`{row[language]}` as problem_trans,
problem
FROM `ords_problem_translations`
WHERE `problem` = %(problem)s
ORDER BY id_ords
"""
        db_res = dbfuncs.mysql_query_fetchall(
            sql,
            {"problem": row[problem]},
        )
        if (not db_res) or len(db_res) == 0:
            logger.debug(f"NOT FOUND: {row[problem_orig]}")
        else:
            results.extend(db_res)

    df_out = pl.DataFrame(data=results).sort("id_ords")
    df_out.write_csv(format_path_out(f"ords_lang_misses_{type}_ids", "csv"))
    logger.debug(f"misses: {df_out.height}")


def get_pipefile():
    return format_path_out("ords_lang_obj_tfidf_cls", "joblib", file_suffix)


def get_clsfile():
    return format_path_out("ords_lang_obj_cls", "joblib", file_suffix)


def get_tdffile():
    return format_path_out("ords_lang_obj_tdif", "joblib", file_suffix)


if __name__ == "__main__":

    # Enable selected funcs from this file to be imported from other files.
    file_suffix = "problem"
    logger = cfg.init_logger(__file__)

    sample = 0.3
    minchars = 12
    maxchars = 65535

    while True:
        eval(
            miscfuncs.exec_opt(
                [
                    f"dump_data(sample={sample}, minchars={minchars}, maxchars={maxchars})",
                    "do_training()",
                    "missing_problem_text('training')",
                    "do_validation()",
                    "missing_problem_text('validation')",
                    "do_detection()",
                ]
            )
        )
