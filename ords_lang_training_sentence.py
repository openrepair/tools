#!/usr/bin/env python3

# An attempt at using the DeepL translated problem text to train an NLP model using scikit.
# See dat/ords_problem_translations.csv and ords_deepl_1setup.py
# WORK IN PROGRESS!

# THIS VERSION SPLITS THE PROBLEM TEXT.
# MORE USEFUL FOR TRAINING.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn import model_selection
from sklearn.model_selection import train_test_split
from joblib import dump
from joblib import load
from nltk import tokenize
import nltk
import polars as pl
from funcs import *

def format_path_out(filename, ext="csv", suffix=""):
    return "{}/{}_{}.{}".format(cfg.OUT_DIR, filename, suffix, ext)


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
        msg = "** TRAIN: classifier best alpha value(s): {}".format(
            multinomial_nb_grid.best_params_
        )
        logger.debug(msg)
        print(msg)
        return multinomial_nb_grid.best_params_["alpha"]
    else:
        return 0.1


# In the case of repair data, ignore acronyms and jargon.
def get_stopwords():
    stopfile = open(cfg.DATA_DIR + "/ords_lang_training_stopwords.txt", "r")
    stoplist = list(stopfile.read().replace("\n", " "))
    stopfile.close()
    return stoplist


# For each language column in the translations table,
# clean and split the `problem` text into sentences
# and label each sentence with the known language.
# Sample for training and validation.
def dump_data(sample=0.3, minchars=12, maxchars=65535):
    # Map the ISO lang codes to the names of the nltk language models.
    langs = {
        "en": "english",
        "de": "german",
        "nl": "dutch",
        "fr": "french",
        "it": "italian",
        "es": "spanish",
        "da": "danish",
    }
    # Read input DataFrame.
    df_in = pl.read_csv(cfg.DATA_DIR + "/ords_problem_translations.csv").filter(
        pl.col("language_known") != pl.lit("??")
    )
    logger.debug("Total translation records: {}".format(df_in.height))
    # Create output DataFrames:
    # problem_orig = problem text before cleaning.
    # problem = translated problem text.
    # sentence = one of the sentences that make up the translated problem text.
    # language = language_known.
    # country = ISO country code.
    cols = {
        "problem_orig": pl.String,
        "problem": pl.String,
        "sentence": pl.String,
        "language": pl.String,
        "country": pl.String,
    }
    df_valid = pl.DataFrame(schema=cols)
    df_train = pl.DataFrame(schema=cols)

    for lang in langs.keys():
        logger.debug("*** LANGUAGE {} ***".format(lang))
        df_lang = pl.DataFrame(schema=cols)
        df_tmp = df_in.select(lang, "country", "problem").rename(
            {"problem": "problem_orig", lang: "problem"}
        )
        df_tmp = textfuncs.clean_text(df_tmp, "problem")
        print("Splitting sentences for lang {}".format(lang))
        for row in df_tmp.iter_rows():
            problem = row[0]
            if len(problem) > 0:
                try:
                    # Split the `problem` string into sentences.
                    sentences = tokenize.sent_tokenize(problem, language=langs[lang])
                    df_tmp = pl.DataFrame(
                        data={
                            "problem_orig": row[2],
                            "problem": problem,
                            "sentence": sentences,
                            "language": lang,
                            "country": row[1],
                        }
                    )
                    df_lang.extend(df_tmp)
                except Exception as error:
                    print(error)
        print("Appending sentences for lang {}".format(lang))
        logger.debug("Total sentences for lang {} : {}".format(lang, df_lang.height))
        df_lang = (
            df_lang.unique()
            .filter(
                pl.col("sentence").str.len_chars().is_between(minchars, maxchars + 1)
            )
            .with_columns(
                pl.col("sentence")
                .str.replace(r"(?i)([\W]{2,})", " ")
                .str.strip_chars()
                .alias("sentence")
            )
        )
        logger.debug(
            "Total usable sentences for lang {} : {}".format(lang, df_lang.height)
        )

        # Take % of the data for validation.
        df_train_tmp, df_valid_tmp = train_test_split(df_lang, test_size=sample)
        logger.debug(
            "Validation data for lang {}: {} ({})".format(
                lang,
                df_valid_tmp.height,
                df_valid_tmp.height / df_lang.height,
            )
        )
        logger.debug(
            "Training data for lang {}: {} ({})".format(
                lang,
                df_train_tmp.height,
                df_train_tmp.height / df_lang.height,
            )
        )

        df_valid.extend(df_valid_tmp)
        df_train.extend(df_train_tmp)

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


# Experiment with classifier/vectorizer.
def experiment():
    data = pl.read_csv(
        format_path_out("ords_lang_data_training", "csv", file_suffix)
    ).drop_nulls(subset="sentence")
    stopwords = get_stopwords()
    column = data["sentence"]
    labels = data["language"]

    vectorizer = TfidfVectorizer()
    if stopwords != False:
        vectorizer.set_params(stop_words=stopwords)
    feature_vects = vectorizer.fit_transform(column)

    # Get the alpha value.
    # Use search=True to find a good value, or False for default.
    # If a better value than default is found, replace default with it.
    alpha = get_alpha(column, labels, feature_vects, search=True)
    logger.debug("** TRAIN : vectorizer ~ shape **")
    logger.debug(feature_vects.shape)
    logger.debug("** TRAIN : vectorizer ~ feature names **")
    logger.debug(vectorizer.get_feature_names_out())

    # Other classifiers are available!
    # https://scikit-learn.org/stable/modules/naive_bayes.html
    # Tuning different classifiers could sway results.

    classifier = MultinomialNB(force_alpha=True, alpha=alpha)

    # Fit the data.
    classifier.fit(feature_vects, labels)
    logger.debug("** TRAIN : classifier: params **")
    logger.debug(classifier.get_params())

    # Get predictions on own features.
    predictions = classifier.predict(feature_vects)
    logger.debug(
        "** TRAIN : classifier: F1 SCORE: {}".format(
            metrics.f1_score(labels, predictions, average="macro")
        )
    )
    logger.debug(predictions)

    # Save the classifier and vectoriser objects for re-use.
    dump(classifier, get_clsfile())
    dump(vectorizer, get_tdffile())

    # Save predictions to 'out' directory in csv format.
    data.loc[:, "prediction"] = predictions
    data.to_csv(
        format_path_out("ords_lang_results_training_tests", "csv", file_suffix),
        index=False,
    )

    # Save prediction misses.
    misses = data[(data["language"] != data["prediction"])]
    misses.to_csv(
        format_path_out("ords_lang_misses_training_tests", "csv", file_suffix),
        index=False,
    )


def do_training():

    data = pl.read_csv(
        format_path_out("ords_lang_data_training", "csv", file_suffix)
    ).drop_nulls(subset="sentence")
    column = data["sentence"]
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
    logger.debug("** TRAIN : F1 SCORE: {}".format(score))

    # Save predictions to 'out' directory in csv format.
    data = data.with_columns(prediction=predictions)
    data.write_csv(format_path_out("ords_lang_results_training", "csv", file_suffix))

    # Save prediction misses.
    misses = data.filter(pl.col("language") != pl.col("prediction"))
    misses.write_csv(format_path_out("ords_lang_misses_training", "csv", file_suffix))


def do_validation(pipeline=True):
    data = pl.read_csv(
        format_path_out("ords_lang_data_validation", "csv", file_suffix)
    ).drop_nulls(subset="sentence")
    column = data["sentence"]
    labels = data["language"]

    logger.debug("** VALIDATE : using pipeline - {}".format(pipeline))
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
    logger.debug("** VALIDATE : F1 SCORE: {}".format(score))
    logger.debug(metrics.classification_report(labels, predictions))

    # Predictions output for inspection.
    data = data.with_columns(prediction=predictions)
    data.write_csv(format_path_out("ords_lang_results_validation", "csv", file_suffix))

    # Prediction misses for inspection.
    misses = data.filter(pl.col("language") != pl.col("prediction"))
    misses.write_csv(format_path_out("ords_lang_misses_validation", "csv", file_suffix))


# Use model on untrained data, with either pipeline or vect/class objects.
def do_detection(pipeline=True):

    data = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
    column = data["problem"]

    logger.debug("** DETECT : using pipeline - {}".format(pipeline))
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

    logger.debug("misses_report: {}".format(type))
    # problem_orig,problem,sentence,language,country,prediction
    df_in = pl.read_csv(
        format_path_out("ords_lang_misses_{}".format(type), "csv", file_suffix)
    )
    cols = df_in.columns
    language = cols.index("language")
    problem = cols.index("problem")
    problem_orig = cols.index("problem_orig")
    prediction = cols.index("prediction")
    results = []
    for row in df_in.iter_rows():
        sql = """
        SELECT
        id_ords,
        country,
        language_known,
        '{0}' as language_trans,
        '{1}' as prediction,
        `{0}` as problem_trans,
        problem
        FROM `ords_problem_translations`
        WHERE `problem` = %(problem)s
        ORDER BY id_ords
        """
        db_res = dbfuncs.mysql_query_fetchall(
            sql.format(row[language], row[prediction]),
            {"problem": row[problem]},
        )
        if (not db_res) or len(db_res) == 0:
            logger.debug("NOT FOUND: {}".format(row[problem_orig]))
        else:
            results.extend(db_res)

    df_out = pl.DataFrame(data=results).sort("id_ords")
    df_out.write_csv(format_path_out("ords_lang_misses_{}_ids".format(type), "csv"))
    logger.debug("misses: {}".format(df_out.height))


# Just checking lengths of sentences sent to classifier.
def misses_by_sentence_length():
    logger.debug("short_misses_report")
    df_t = pl.read_csv(
        format_path_out("ords_lang_misses_training", "csv", file_suffix)
    )[["sentence"]]
    df_v = pl.read_csv(
        format_path_out("ords_lang_misses_validation", "csv", file_suffix)
    )[["sentence"]]
    df_out = (
        pl.concat([df_t, df_v])
        .unique()
        .with_columns(chars=pl.col("sentence").str.len_chars())
    )
    df_out.write_csv(format_path_out("ords_lang_misses_short", "csv", file_suffix))
    logger.debug("misses short: {}".format(df_out.height))
    logger.debug(
        df_out.describe(
            percentiles=[0.1, 0.3, 0.5, 0.7, 0.9],
        )
    )


def get_pipefile():
    return format_path_out("ords_lang_obj_tfidf_cls", "joblib", file_suffix)


def get_clsfile():
    return format_path_out("ords_lang_obj_cls", "joblib", file_suffix)


def get_tdffile():
    return format_path_out("ords_lang_obj_tdif", "joblib", file_suffix)


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
        1: "dump_data(sample=0.3, minchars=12, maxchars=65535)",
        2: "do_training()",
        3: "missing_problem_text('training')",
        4: "do_validation()",
        5: "missing_problem_text('validation')",
        6: "misses_by_sentence_length()",
        7: "do_detection()",
        8: "experiment()",
    }


if __name__ == "__main__":

    # Enable selected funcs from this file to be imported from other files.
    file_suffix = "sentence"
    logger = cfg.init_logger(__file__)

    nltk.download("punkt")
    exec_opt(get_options())
