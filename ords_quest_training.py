#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn import model_selection
from joblib import dump
from joblib import load

"""
A rudimentary attempt at using Quest data to train an NLP model using scikit-learn.

Quests are citizen-science type microtasks that ask humans to evaluate and classify repair data.
Most quests aim to determine a set of common fault types for a given product category.
See the dat/quests/README.md for details.
Some of the problems of using the quest data for training and validation are that:
  . Early quests did not filter out very poor quality problem text.
  . Quest data is multi-lingual and NLP tends to require a single language.
  . Human evaluation was not always conclusive or accurate when problem text was ambiguous or poorly translated.
Consequently, after cleaning and filtering, the data left for training is not really sufficient.
The training data may benefit from manual curation. (Also cleaning stopwords #todo)

The following is a live data "test":
1. Selected quest no. 5 "DustUp" as it has decent quality data.
2. Removed the validation step and used all of the quest data for training. (English language, 738 records)
3. Used the model on all ORA "Vacuum" records from countries GBP and USA. (English language, 1446 records)
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

"""


def dump_data(data, countries):

    logger.debug('*** RAW DATA ***')
    logger.debug(len(data))
    # Filter out NaNs in problem column.
    data.dropna(axis='rows', subset=[
        'problem'], inplace=True, ignore_index=True)
    logger.debug('*** NO NAN DATA ***')
    logger.debug(len(data))
    # Filter for records from the UK/USA as they will mostly be in English.
    data = data[data['country'].isin(countries)]
    logger.debug('*** COUNTRY DATA ***')
    logger.debug(len(data))
    # Filter for string length. Earlier quests often contained poor quality problem text.
    # However, this can leave almost no data for training.
    # data = data[(data['problem'].apply(lambda x: len(str(x)) > 8))]
    # logger.debug('*** LENGTH DATA ***')
    # logger.debug(len(data))

    # Select useful columns and rows.
    data = data.reindex(
        columns=['id_ords', 'fault_type', 'problem'])

    # Take % of the data for validation.
    data_val = data.groupby(['fault_type']).sample(
        frac=0.3, replace=False, random_state=1)
    logger.debug('*** VALIDATION DATA ***')
    logger.debug(len(data_val))
    logger.debug(len(data_val) / len(data))

    # Remaining % of the data is for training.
    data_train = data.drop(data_val.index)
    logger.debug('*** TRAINING DATA ***')
    logger.debug(len(data_train))
    logger.debug(len(data_train) / len(data))

    # Save the data to the 'out' directory in csv format for use later.
    data_train.to_csv(format_path('ords_quest_training_data'), index=False)
    data_val.to_csv(format_path('ords_quest_validation_data'), index=False)


# Most of the quest data returns an alpha of 0.01.
# One of the quests returns a slightly higher alpha.
# Use this to check for best values.
# It will slow down execution considerably.
def get_alpha(data, labels, vects, search=False, refit=False):
    if search:
        # Try out some alpha values to find the best one for this data.
        params = {'alpha': [0, 0.001, 0.01, 0.1, 5, 10], }
        # Instantiate the search with the model we want to try and fit it on the training data.
        cvval = 5
        if len(data) < cvval:
            cvval = len(data)
        multinomial_nb_grid = model_selection.GridSearchCV(MultinomialNB(
        ), param_grid=params, scoring='f1_macro', n_jobs=-1, cv=cvval, refit=False, verbose=2)
        multinomial_nb_grid.fit(vects, labels)
        logger.debug(
            '** TRAIN {}: classifier best alpha value(s): {}'.format(quest, multinomial_nb_grid.best_params_))
        print(
            '** TRAIN {}: classifier best alpha value(s): {}'.format(quest, multinomial_nb_grid.best_params_))
        # This function could return the classifier instead of just the alpha param.
        # if refit == True:
        #     return multinomial_nb_grid.best_estimator_
        return multinomial_nb_grid.best_params_['alpha']
    else:
        return 0.01


def do_training(data):

    column = data.problem
    labels = data.fault_type

    vectorizer = TfidfVectorizer()
    feature_vects = vectorizer.fit_transform(column)

    # Get the alpha value. Use search=True to find a good value, or False for default.
    alpha = get_alpha(column, labels, feature_vects, search=False)
    # Other classifiers are available!
    nb_classifier = MultinomialNB(
        force_alpha=True, alpha=alpha)

    logger.debug('** TRAIN : vectorizer ~ shape **')
    logger.debug(feature_vects.shape)
    logger.debug('** TRAIN : vectorizer ~ feature names **')
    logger.debug(vectorizer.get_feature_names_out())

    # Fit the data.
    nb_classifier.fit(feature_vects, labels)
    logger.debug('** TRAIN : nb_classifier: params **')
    logger.debug(nb_classifier.get_params())

    # Get predictions.
    preds = nb_classifier.predict(feature_vects)
    logger.debug('** TRAIN : nb_classifier: F1 SCORE: {}'.format(
        metrics.f1_score(labels, preds, average='macro')))
    logger.debug(preds)

    # Save the classifier and vectoriser objects for use later.
    dump(nb_classifier, clsfile)
    dump(vectorizer, tdffile)

    # Save predictions to 'out' directory in csv format.
    data.loc[:, 'prediction'] = preds
    data.to_csv(format_path('ords_quest_training_results'), index=False)

    # Save prediction misses.
    misses = data[(data['fault_type'] != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_quest_training_misses'), index=False)


def do_validation(data):

    column = data.problem
    labels = data.fault_type

    # Get the classifier and vectoriser that were fitted for this task.
    nb_classifier = load(clsfile)
    logger.debug('** VAL : classifier {}'.format(type(nb_classifier)))
    vectorizer = load(tdffile)
    logger.debug('** VAL : vectorizer {}'.format(type(vectorizer)))

    # Get the predictions
    feature_vects = vectorizer.transform(column)
    preds = nb_classifier.predict(feature_vects)
    logger.debug('** VAL : nb_classifier: F1 SCORE: {}'.format(
        metrics.f1_score(labels, preds, average='macro')))
    logger.debug(metrics.classification_report(
        labels, preds))

    # Predictions output for inspection.
    data.loc[:, 'prediction'] = preds
    data.to_csv(format_path('ords_quest_validation_results'), index=False)

    # Prediction misses for inspection.
    misses = data[(data['fault_type'] != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_quest_validation_misses'), index=False)


def do_test(data, category, countries):

    data.dropna(axis='rows', subset=[
        'problem'], inplace=True, ignore_index=True)
    data = data[(data['product_category'] == category)
                & (data['country'].isin(countries))]

    column = data.problem

    # Get the classifier and vectoriser that were fitted for this task.
    nb_classifier = load(clsfile)
    logger.debug('** TEST : classifier {}'.format(type(nb_classifier)))
    vectorizer = load(tdffile)
    logger.debug('** TEST : vectorizer {}'.format(type(vectorizer)))

    # Get the predictions.
    feature_vects = vectorizer.transform(column)
    preds = nb_classifier.predict(feature_vects)

    # Predictions output.
    data.loc[:, 'prediction'] = preds
    data.to_csv(format_path('ords_quest_test_results'), index=False)


def format_path(filename, ext='csv'):
    return '{}/{}_{}.{}'.format(pathfuncs.OUT_DIR, filename, quest, ext)


# START

# Available quest datasets.
# See dat/quests for details.
quests = [
    tuple(['Compcat-Laptops', 'computers/compcat_laptops.csv', 'Laptop']),
    tuple(['Compcat-Desktops', 'computers/compcat_laptops.csv', 'Desktop PC']),
    tuple(['MobiFix', 'mobiles/mobifix.csv', 'Mobiles']),
    tuple(['PrintCat', 'printers/printcat.csv', 'Printer/scanner']),
    tuple(['TabiCat', 'tablets/tabicat.csv', 'Tablet']),
    tuple(['DustUp', 'vacuums/dustup.csv', 'Vacuum'])
]

# Select a dataset 0 to 5.
quest, path, category = quests[5]

logger = logfuncs.init_logger('ords_quest_training_' + quest)

# Path to the classifier and vectoriser objects.
clsfile = format_path('ords_quest_obj_nbcl', 'joblib')
tdffile = format_path('ords_quest_obj_tdif', 'joblib')

# Initialise the training/validation datasets.
data = pd.read_csv(pathfuncs.DATA_DIR + '/quests/' + path,
                   dtype=str, keep_default_na=False, na_values="")
dump_data(data, countries=['GBR', 'USA'])

# Use the dumped training dataset.
data = pd.read_csv(format_path('ords_quest_training_data'),
                   dtype=str, keep_default_na=False, na_values="")
do_training(data)

# Use the dumped validation dataset.
data = pd.read_csv(format_path('ords_quest_validation_data'),
                   dtype=str, keep_default_na=False, na_values="")
do_validation(data)

# Read the entire ORDS export.
data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
# The function will filter the data for the appropriate product_category.
# The subset will contain the training and validation data
# but does not have a fault_type column and id_ords will not match.
# Early ORDS exports did not have permanent unique identifiers.
do_test(data, category, countries=['GBR', 'USA'])
