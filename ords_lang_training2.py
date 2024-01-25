#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn import model_selection
from sklearn.model_selection import train_test_split
from joblib import dump
from joblib import load
import nltk

nltk.download("punkt")

logger = logfuncs.init_logger(__file__)

# An attempt at using the DeepL translated problem text to train an NLP model using scikit.
# See dat/ords_problem_translations.csv and ords_deepl_1setup.py
# WORK IN PROGRESS!


def format_path(filename, ext="csv"):
    return "{}/{}.{}".format(pathfuncs.OUT_DIR, filename, ext)


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
    df_train.to_csv(format_path("ords_lang_data_training2"), index=False)
    df_valid.to_csv(format_path("ords_lang_data_validation2"), index=False)


def clean_text(data, dedupe=True, dropna=True):
    # Remove HTML symbols (&gt; features a lot)
    data.replace(
        {"problem": r"(?i)(&[\w\s]+;)"},
        {"problem": ""},
        regex=True,
        inplace=True,
    )
    # Remove weight values (0.5kg, 5kg, 5 kg, .5kg etc.)
    data.replace(
        {"problem": r"(?i)(([0-9]+)?\.?[0-9\s]+kg)"},
        {"problem": ""},
        regex=True,
        inplace=True,
    )
    # Remove strange codes often found prefixing `problem` strings.
    data.replace(
        {"problem": r"(?i)^(\W|\d+)([\d|\W]+)?"},
        {"problem": ""},
        regex=True,
        inplace=True,
    )
    # Remove multiple punctuation characters.
    data.replace(
        {"problem": r"(?i)([\.\?\-*,;:]{2,})"},
        {"problem": " "},
        regex=True,
        inplace=True,
    )
    # Make sure there is always a space after a period, else sentences won't be split.
    data.replace(
        {"problem": r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"},
        {"problem": "\\2. \\3"},
        regex=True,
        inplace=True,
    )
    # Trim whitespace from `problem` strings.
    data["problem"].str.strip()
    if dropna:
        # Drop `problem` values that may be empty after the replacements and trimming.
        data.dropna(subset=["problem"], inplace=True)
        print(data.index.size)
    if dedupe:
        # Dedupe the `problem` values.
        data.drop_duplicates(subset=["problem"], inplace=True)
        print(data.index.size)
    return data


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
    stopfile = open(pathfuncs.DATA_DIR + "/ords_lang_training_stopwords.txt", "r")
    stoplist = list(stopfile.read().replace("\n", " "))
    stopfile.close()
    return stoplist


# Experiment with classifier/vectorizer.
def experiment():
    data = pd.read_csv(format_path("ords_lang_data_training2"), dtype=str).dropna()

    stopwords = get_stopwords()
    column = data.problem
    labels = data.language

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

    classifier = MultinomialNB(force_alpha=True, alpha=alpha)

    # Other classifiers are available!
    # https://scikit-learn.org/stable/modules/naive_bayes.html
    # Tuning different classifiers could sway results.
    # from sklearn.naive_bayes import ComplementNB
    # classifier = ComplementNB(
    #     force_alpha=True, alpha=alpha)

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
    dump(classifier, clsfile)
    dump(vectorizer, tdffile)

    # Save predictions to 'out' directory in csv format.
    data.loc[:, "prediction"] = predictions
    data.to_csv(format_path("ords_lang_results_training2_tests"), index=False)

    # Save prediction misses.
    misses = data[(data["language"] != data["prediction"])]
    misses.to_csv(format_path("ords_lang_misses_training2_tests"), index=False)


def do_training():
    data = pd.read_csv(format_path("ords_lang_data_training2"), dtype=str).dropna()

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
    dump(pipe, pipefile)
    predictions = pipe.predict(column)
    score = metrics.f1_score(labels, predictions, average="macro")
    logger.debug("** TRAIN : F1 SCORE: {}".format(score))

    # Save predictions to 'out' directory in csv format.
    data.loc[:, "prediction"] = predictions
    data.to_csv(format_path("ords_lang_results_training2"), index=False)

    # Save prediction misses.
    misses = data[(data["language"] != data["prediction"])]
    misses.to_csv(format_path("ords_lang_misses_training2"), index=False)


def do_validation(pipeline=True):
    data = pd.read_csv(format_path("ords_lang_data_validation2"), dtype=str).dropna()

    column = data.problem
    labels = data.language

    logger.debug("** VALIDATE : using pipeline - {}".format(pipeline))
    if pipeline:
        # Use the pipeline that was fitted for this task.
        pipe = load(pipefile)
        predictions = pipe.predict(data.problem)
    else:
        # Use the classifier and vectoriser that were fitted for this task.
        classifier = load(clsfile)
        vectorizer = load(tdffile)
        feature_vects = vectorizer.transform(column)
        predictions = classifier.predict(feature_vects)

    score = metrics.f1_score(labels, predictions, average="macro")
    logger.debug("** VALIDATE : F1 SCORE: {}".format(score))
    logger.debug(metrics.classification_report(labels, predictions))

    # Predictions output for inspection.
    data.loc[:, "prediction"] = predictions
    data.to_csv(format_path("ords_lang_results_validation2"), index=False)

    # Prediction misses for inspection.
    misses = data[(data.language != data["prediction"])]
    misses.to_csv(format_path("ords_lang_misses_validation2"), index=False)


# Use model on untrained data, with either pipeline or vect/class objects.
def do_detection(pipeline=True):
    data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
    data.dropna(axis="rows", subset=["problem"], inplace=True, ignore_index=True)
    column = data.problem
    logger.debug("** DETECT : using pipeline - {}".format(pipeline))
    if pipeline:
        # Use the pipeline that was fitted for this task.
        pipe = load(pipefile)
        predictions = pipe.predict(data.problem)
    else:
        # Use the classifier and vectoriser that were fitted for this task.
        classifier = load(clsfile)
        vectorizer = load(tdffile)
        feature_vects = vectorizer.transform(column)
        predictions = classifier.predict(feature_vects)

    # Predictions output.
    data.loc[:, "prediction"] = predictions
    data = data.reindex(columns=["id", "problem", "prediction"])
    data.to_csv(format_path("ords_lang_results_detection2"), index=False)
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

    df_out = pd.DataFrame(data=results)
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
FROM `ords_problem_translations_NEW`
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


# START

# Path to the model objects for dump/load.
clsfile = format_path("ords_lang_obj2_cls", "joblib")
tdffile = format_path("ords_lang_obj2_tdif", "joblib")
pipefile = format_path("ords_lang_obj2_tfidf_cls", "joblib")

options = {
    0: "exit()",
    1: "dump_data(sample=0.3, minchars=12, maxchars=65535)",
    2: "do_training()",
    3: "misses_report('training')",
    4: "do_validation()",
    5: "misses_report('validation')",
    6: "do_detection()",
    7: "experiment()",
    8: "charcheck()",
}
exec_opt(options)
