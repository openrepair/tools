#!/usr/bin/env python3

"""
Another rudimentary attempt at using Quest data to train an NLP model using scikit-learn.
This script is a slimmed-down version of the quest training script for a single quest - DustUp.
It uses the language training model to filter the input for English only,
as only English is supported by the stopwords and tokenizer.
It cleans the input and uses a pipeline and manually created validation dataset.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from joblib import dump
from joblib import load
import nltk
import re
import polars as pl
from funcs import *

nltk.download("wordnet")


def get_datasets(product_category_id, language="en"):

    # This is the latest entire ORDS dataset.
    logger.debug("*** ALL ORDS DATA ***")
    alldata = (
        ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
        .filter(pl.col("product_category_id") == product_category_id)
        .drop_nulls(subset="problem")
        .select(pl.col("id", "problem"))
    )

    # This file holds the results of the quest.
    logger.debug("*** QUEST DATA ***")
    questdata = pl.read_csv(ordsfuncs.csv_path_quests("vacuums/dustup")).rename(
        {"id_ords": "id"}
    )
    logger.debug(questdata)

    # This file was created by manual review of some records not included in the quest.
    logger.debug("*** VALIDATION DATA ***")
    valdata = pl.read_csv(ordsfuncs.csv_path_quests("vacuums/dustup_validate_en"))
    logger.debug(valdata)

    # Join the datasets.
    logger.debug("*** JOINED DATA ***")
    jdata = (
        alldata.join(questdata, on="id", how="left")
        .join(valdata, on="id", how="left", suffix="_v")
        .rename({"fault_type": "fault_type_q"})
    )
    logger.debug(jdata.select(pl.col("id", "fault_type_q", "fault_type_v")))

    logger.debug("*** NEW DATA ***")
    foo = textfuncs.clean_text(
        jdata.filter(
            (pl.col("fault_type_q").is_null()) & (pl.col("fault_type_v").is_null())
        ),
        "problem",
    )
    newdata = detect_language(foo).filter(pl.col("language") == language)
    logger.debug(newdata)

    logger.debug("*** VAL DATA ***")
    valdata = (
        detect_language(
            textfuncs.clean_text(jdata.filter((pl.col("fault_type_v").is_not_null())))
        )
        .filter(pl.col("language") == language)
        .rename({"fault_type_v": "fault_type"})
        .drop("fault_type_q")
    )
    logger.debug(valdata)

    logger.debug("*** QUEST DATA ***")
    questdata = (
        detect_language(
            textfuncs.clean_text(jdata.filter(pl.col("fault_type_q").is_not_null()))
        )
        .filter(pl.col("language") == language)
        .rename({"fault_type_q": "fault_type"})
        .drop("fault_type_v")
    )
    logger.debug(questdata)

    return {
        "questdata": questdata,
        "valdata": valdata,
        "data": newdata,
    }


# Use a pre-trained model to detect and set the language.
# This should be more accurate than DeepL's language detection, though model still being refined.
# Requires that `ords_lang_training.py` has created the model object.
def detect_language(data):

    lang_obj_path = f"{cfg.OUT_DIR}/ords_lang_obj_tfidf_cls_sentence.joblib"
    if not pathfuncs.check_path(lang_obj_path):
        print(f"LANGUAGE DETECTOR ERROR: MODEL NOT FOUND at {lang_obj_path}")
        print("TO FIX THIS EXECUTE: ords_lang_training_sentence.py")
        data = data.with_columns(language=pl.lit("??"))
    else:
        model = load(lang_obj_path)
        data = data.with_columns(language=model.predict(data["problem"]))

    return data


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        self.rx = re.compile("[\W\d_]")

    def __call__(self, doc):
        return [
            self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))
        ]


def get_stopwords():
    stopfile1 = open(f"{cfg.DATA_DIR}/stopwords-english.txt", "r")
    stopfile2 = open(f"{cfg.DATA_DIR}/stopwords-english-repair.txt", "r")
    stoplist = stopfile1.read().replace("\n", " ") + stopfile2.read().replace("\n", " ")
    stopfile1.close()
    stopfile2.close()
    return stoplist


def do_training(questdata):
    tokenizer = LemmaTokenizer()
    pipe = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    tokenizer=tokenizer, stop_words=tokenizer(get_stopwords())
                ),
            ),
            ("clf", MultinomialNB(force_alpha=True, alpha=0.01)),
        ]
    )
    pipe.fit(questdata["problem"], questdata["fault_type"])
    dump(pipe, pipefile)
    predictions = pipe.predict(questdata["problem"])
    score = metrics.f1_score(questdata["fault_type"], predictions, average="macro")
    logger.debug(f"** TRAINING : F1 SCORE: {score}")
    questdata = questdata.with_columns(prediction=predictions)
    questdata.write_csv(f"{cfg.OUT_DIR}/ords_quest_vacuum_training_results.csv")

    logger.debug("** TRAINING MISSES **")
    misses = questdata.filter(pl.col("language") != pl.col("prediction"))
    logger.debug(misses)
    misses.write_csv(f"{cfg.OUT_DIR}/ords_quest_vacuum_training_misses.csv")


def do_validation(valdata):

    pipe = load(pipefile)
    predictions = pipe.predict(valdata["problem"])
    score = metrics.f1_score(valdata["fault_type"], predictions, average="macro")
    logger.debug(f"** VALIDATION : F1 SCORE: {score}")
    logger.debug(metrics.classification_report(valdata["fault_type"], predictions))

    valdata = valdata.with_columns(prediction=predictions)
    valdata.write_csv(f"{cfg.OUT_DIR}/ords_quest_vacuum_validation_results.csv")

    logger.debug("** VALIDATION MISSES **")
    misses = valdata.filter(pl.col("fault_type") != pl.col("prediction"))
    logger.debug(misses)
    misses.write_csv(f"{cfg.OUT_DIR}/ords_quest_vacuum_validation_misses.csv")


def do_test(data):

    pipe = load(pipefile)
    data = data.with_columns(prediction=pipe.predict(data["problem"]))
    data.write_csv(f"{cfg.OUT_DIR}/ords_quest_vacuum_test_results.csv")


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    pipefile = f"{cfg.OUT_DIR}/ords_quest_vacuum_obj_tfidf_cls.joblib"

    datasets = get_datasets(product_category_id=34, language="en")

    do_training(datasets["questdata"])

    do_validation(datasets["valdata"])

    do_test(datasets["data"])
