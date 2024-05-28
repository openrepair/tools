#!/usr/bin/env python3


"""
A rudimentary attempt at using Quest data to train an NLP model using scikit-learn.

Quests are citizen-science type microtasks that ask humans to evaluate and classify repair data.
Most quests aim to determine a set of common fault types for a given product category.
See the dat/quests/README.md for details.
Some of the problems of using the quest data for training and validation are that:
  . Early quests did not filter out very poor quality problem text at all.
  . Human evaluation was not always conclusive or accurate when problem text was ambiguous or poorly translated.
  . The problem text is multi-lingual and training works best with a single language at a time.
  . The fault types (training labels) are imprecise "buckets" and better values could be gleaned after the quest.
Consequently, after cleaning and filtering, the data left for training is not really sufficient.
Nonetheless the quests have been useful learning exercises that could inform future quests.

The following "test" was conducted on the 202303 dataset:
1. Selected quest no. 5 "DustUp" as it has decent quality data compared to previous quests.
2. Removed the validation step and used all of the GBR/USA quest data for training. (738 records)
3. Used the model on all ORA "Vacuum" GBR/USA records. (1446 records)
4. Exported the results to a spreadsheet and manually reviewed the predictions, excluding records used in training.
5. Found that I agreed with 60% of the predictions and that this was roughly reflected across all fault types:
    58.67%	Power/battery
    64.17%	Blockage
    67.39%	Poor data
    58.43%	Motor
    65.08%	Cable/cord
    55.81%	Internal damage
    56.41%	Button/switch
    60.61%	Brush
    71.43%	Filter
    57.89%	External damage
    50.00%	Hose/tube/pipe
    46.15%	Other
    41.67%	Overheating
    50.00%	Dustbag/canister
    33.33%	Accessories/attachments
    50.00%	Wheels/rollers
6. Refactored the script to optionally train with "clean" data, i.e. ignoring punctuation and stopwords.
7. Retrained without validation, using all of the GBR/USA quest data.
8. Compared new predictions with opinions given in first manual review.
9. Found that yet again human opinion agreed with 60% of predictions, although the spread had changed slightly.
    60.43%	Power/battery	        (+1.76%)
    63.25%	Blockage                (-0.92%)
    63.73%	Poor data               (-3.67%)
    60.00%	Motor	                (+1.57%)
    70.49%	Cable/cord              (+5.41%)
    55.56%	Internal damage	        (-0.26%)
    55.26%	Brush	                (-5.34%)
    60.61%	Button/switch	        (+4.20%)
    58.33%	Filter	                (-13.10%)
    75.00%	Hose/tube/pipe	        (+25.00%)
    62.50%	External damage	        (+4.61%)
    38.46%	Other	                (-7.69%)
    36.36%	Wheels/rollers	        (-13.64%)
    37.50%	Overheating             (-4.17%)
    40.00%	Accessories/attachments	(+6.67%)
    50.00%	Dustbag/canister        (0.00%)
10. It is worth noting that the % difference represents only a handful of records (<7) for each fault type (avg=0).
11. Conclusion: need more/better data and better `fault_type` labels.
    Would be worth curating a custom vocabulary for each `product_category`.
12. Implemented improved list of stopwords, including corpus-specific, plus improved lemma char filtering.
13. Retrained without validation, using all of the GBR/USA quest data.
14. Compared new predictions with opinions given in first manual review.
15. Found that human opinion agreed with 66% of predictions.
    61.94%	Poor data               (-5.45%)
    70.18%	Power/battery           (+11.51%)
    69.52%	Blockage                (+5.36%)
    75.00%	Motor                   (+16.57%)
    76.27%	Cable/cord              (+11.19%)
    65.79%	Internal damage         (+9.98%)
    63.16%	Brush                   (+2.55%)
    70.59%	Button/switch           (+14.18%)
    65.63%	Filter                  (-5.80%)
    72.22%	Hose/tube/pipe          (+22.22%)
    58.82%	External damage         (+0.93%)
    52.94%	Other                   (+6.79%)
    53.33%	Wheels/rollers          (+3.33%)
    50.00%	Overheating             (+8.33%)
    22.22%	Accessories/attachments	(-11.11%)
    14.29%	Dustbag/canister        (-35.71%)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn import model_selection
from sklearn.model_selection import train_test_split
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from joblib import dump
from joblib import load
import re
import polars as pl
from funcs import *


# Split value is the fraction to take for validation, e.g. 0.3
def dump_data(data, countries, sample=0):

    logger.debug("*** RAW DATA ***")
    logger.debug(data.height)
    data = (
        data.filter(pl.col("country").is_in(countries))
        .drop_nulls(subset="problem")
        .select(pl.col("id_ords", "fault_type", "problem"))
    )
    logger.debug("*** FILTERED DATA ***")
    logger.debug(data.height)

    if sample != 0:
        data_train, data_val = train_test_split(data, test_size=sample)
        logger.debug("*** VALIDATION DATA ***")
        logger.debug(data_val.height)
        logger.debug(data_val.height / data.height)
    else:
        data_val = pl.DataFrame()
        data_train = data

    logger.debug("*** TRAINING DATA ***")
    logger.debug(data_train.height)
    logger.debug(data_train.height / data.height)

    # Save the data to the 'out' directory in csv format for use later.
    data_train.write_csv(format_path("ords_quest_training_data"))
    data_val.write_csv(format_path("ords_quest_validation_data"))


# Most of the quest data returns an alpha of 0.01.
# One of the quests returns a slightly higher alpha.
# Use this to check for best values.
# It will slow down execution considerably.
def get_alpha(data, labels, vects, search=False, refit=False):
    if search:
        # Try out some alpha values to find the best one for this data.
        params = {
            "alpha": [0, 0.001, 0.01, 0.1, 5, 10],
        }
        # Instantiate the search with the model we want to try and fit it on the training data.
        cvval = 5
        if data.height < cvval:
            cvval = data.height
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
        msg = "** TRAIN {}: classifier best alpha value(s): {}".format(
            quest, multinomial_nb_grid.best_params_
        )
        logger.debug(msg)
        print(msg)
        return multinomial_nb_grid.best_params_["alpha"]
    else:
        return 0.01


# Required if cleaning the training data.
class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        self.rx = re.compile("[\W\d_]")

    def __call__(self, doc):
        return [
            self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))
        ]


def get_stopwords():
    stopfile1 = open(cfg.DATA_DIR + "/stopwords-english.txt", "r")
    stopfile2 = open(cfg.DATA_DIR + "/stopwords-english-repair.txt", "r")
    stoplist = stopfile1.read().replace("\n", " ") + stopfile2.read().replace("\n", " ")
    stopfile1.close()
    stopfile2.close()
    return stoplist


def do_training(data, tokenizer=False, stopwords=False, vocabulary=False):

    column = data["problem"]
    labels = data["fault_type"]

    vectorizer = TfidfVectorizer()

    # Ignore punctuation, tokenize stop words.
    if tokenizer != False:
        vectorizer.set_params(tokenizer=tokenizer)

    # Ignore punctuation, if tokenizer then must tokenize stop words.
    if stopwords != False:
        if tokenizer != False:
            stopwords = tokenizer(stopwords)
        else:
            stopwords = list(stopwords)

        vectorizer.set_params(stop_words=stopwords)

    if vocabulary != False:
        vectorizer.vocabulary_ = vocabulary
        logger.debug(vectorizer.vocabulary_)

    logger.debug(vectorizer.get_stop_words())
    feature_vects = vectorizer.fit_transform(column)

    # Get the alpha value. Use search=True to find a good value, or False for default.
    alpha = get_alpha(column, labels, feature_vects, search=False)
    # Other classifiers are available!
    nb_classifier = MultinomialNB(force_alpha=True, alpha=alpha)

    logger.debug("** TRAIN : vectorizer ~ shape **")
    logger.debug(feature_vects.shape)
    logger.debug("** TRAIN : vectorizer ~ feature names **")
    logger.debug(vectorizer.get_feature_names_out())

    # Fit the data.
    nb_classifier.fit(feature_vects, labels)
    logger.debug("** TRAIN : nb_classifier: params **")
    logger.debug(nb_classifier.get_params())

    # Get predictions.
    preds = nb_classifier.predict(feature_vects)
    logger.debug(
        "** TRAIN : nb_classifier: F1 SCORE: {}".format(
            metrics.f1_score(labels, preds, average="macro")
        )
    )
    logger.debug(preds)

    # Save the classifier and vectoriser objects for use later.
    dump(nb_classifier, clsfile)
    dump(vectorizer, tdffile)

    # Save predictions to 'out' directory in csv format.
    data = data.with_columns(prediction=preds)
    data.write_csv(format_path("ords_quest_training_results"))

    # Save prediction misses.
    misses = data.filter(pl.col("fault_type") != pl.col("prediction"))
    logger.debug(misses)
    misses.write_csv(format_path("ords_quest_training_misses"))


def do_validation(data):

    column = data["problem"]
    labels = data["fault_type"]

    # Get the classifier and vectoriser that were fitted for this task.
    nb_classifier = load(clsfile)
    logger.debug("** VAL : classifier {}".format(type(nb_classifier)))
    vectorizer = load(tdffile)
    logger.debug("** VAL : vectorizer {}".format(type(vectorizer)))

    # Get the predictions
    feature_vects = vectorizer.transform(column)
    preds = nb_classifier.predict(feature_vects)
    logger.debug(
        "** VAL : nb_classifier: F1 SCORE: {}".format(
            metrics.f1_score(labels, preds, average="macro")
        )
    )
    logger.debug(metrics.classification_report(labels, preds))

    # Predictions output for inspection.
    data = data.with_columns(prediction=preds)
    data.write_csv(format_path("ords_quest_validation_results"))

    # Prediction misses for inspection.
    misses = data.filter(pl.col("fault_type") != pl.col("prediction"))
    logger.debug(misses)
    misses.write_csv(format_path("ords_quest_validation_misses"))


def do_test(data, category, countries):

    data.filter(
        (pl.col("product_category") == category) & (pl.col("country").is_in(countries))
    ).drop_nulls(subset="problem")

    column = data["problem"]

    # Get the classifier and vectoriser that were fitted for this task.
    nb_classifier = load(clsfile)
    logger.debug("** TEST : classifier {}".format(type(nb_classifier)))
    vectorizer = load(tdffile)
    logger.debug("** TEST : vectorizer {}".format(type(vectorizer)))

    # Get the predictions.
    feature_vects = vectorizer.transform(column)
    preds = nb_classifier.predict(feature_vects)

    # Predictions output.
    data = data.with_columns(prediction=preds)
    data.write_csv(format_path("ords_quest_test_results"))


def format_path(filename, ext="csv"):
    return "{}/{}_{}.{}".format(cfg.OUT_DIR, filename, quest, ext)


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    # Available quest datasets.
    # See dat/quests for details.
    quests = [
        tuple(["Compcat-Laptops", "computers/compcat_laptops", "Laptop"]),
        tuple(["Compcat-Desktops", "computers/compcat_laptops", "Desktop PC"]),
        tuple(["MobiFix", "mobiles/mobifix", "Mobiles"]),
        tuple(["PrintCat", "printers/printcat", "Printer/scanner"]),
        tuple(["TabiCat", "tablets/tabicat", "Tablet"]),
        tuple(["DustUp", "vacuums/dustup", "Vacuum"]),
    ]

    # Select a dataset 0 to 5.
    quest, path, category = quests[5]

    logger = cfg.init_logger("ords_quest_training_" + quest)

    # Path to the classifier and vectoriser objects for dump/load.
    clsfile = format_path("ords_quest_obj_nbcl", "joblib")
    tdffile = format_path("ords_quest_obj_tdif", "joblib")

    # Quest data is multi-lingual and NLP tends to require a single language.
    # Using English stopwords/vocabulary will require English language text.
    # Filter for subset of records with English language text.
    iso_list = ["GBR", "USA"]
    # Other countries with en lang `problem` (only a few dozen more records)
    # ['AUS', 'IRL', 'ISL', 'JEY', 'NOR', 'NZL', 'SWE']
    # To Do: refactor to use the language detector.

    # Get vocabulary for `product_category` from list of terms after stopwords extracted.
    # See `ords_extract_vocabulary.py`
    vocabulary = False
    # vocabulary = list(
    #     pl.read_csv(cfg.OUT_DIR + "/ords_vocabulary_problem.csv")
    #     .filter(pl.col("product_category") == category)
    #     .group_by(["term"])
    # )

    # Use stopwords?
    stopwords = False
    # stopwords = get_stopwords()

    # Use tokenisation?
    tokenizer = False
    # tokenizer = LemmaTokenizer()

    # # Initialise the training and (optional) validation datasets.
    # ordsfuncs.csv_path_quests + path
    data = pl.read_csv(ordsfuncs.csv_path_quests(path))

    # Do validation step?
    validate = False
    # If validating, take a fraction of corpus, e.g. 0.3
    sample = 0

    logger.debug("*** quest={} ***".format(quest))
    logger.debug("*** countries={} ***".format(iso_list))
    logger.debug("*** validate={} ***".format(validate))
    logger.debug("*** splitval={} ***".format(sample))
    logger.debug("*** vocabulary={} ***".format(vocabulary))
    logger.debug("*** stopwords={} ***".format(stopwords))
    logger.debug("*** tokenizer={} ***".format(tokenizer))

    dump_data(data, iso_list, sample)

    # Use the dumped training dataset.
    data = pl.read_csv(format_path("ords_quest_training_data"))
    do_training(data, tokenizer=tokenizer, stopwords=stopwords, vocabulary=vocabulary)

    if validate:
        # Use the dumped validation dataset or provide other dataset.
        data = pl.read_csv(format_path("ords_quest_validation_data"))
        do_validation(data)

    # Read the entire ORDS export.
    data = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
    # The function will filter the data for the appropriate product_category.
    # The subset will contain the training and validation data
    # but does not have a fault_type column and id_ords may not match.
    # Early ORDS exports did not have permanent unique identifiers.
    do_test(data, category, iso_list)
