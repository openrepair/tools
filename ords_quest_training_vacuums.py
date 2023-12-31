#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from joblib import dump
from joblib import load


"""
Another rudimentary attempt at using Quest data to train an NLP model using scikit-learn.
This script is a slimmed-down version of the quest training script for a single quest - DustUp.
It uses the language training model to filter the input for English only,
as only English is supported by the stopwords and tokenizer.
It cleans the input and uses a pipeline and manually created validation dataset.
"""

def get_datasets(product_category_id, language='en'):

    # This is the latest entire ORDS dataset.
    alldata = pd.read_csv(pathfuncs.path_to_ords_csv())
    alldata = alldata.loc[alldata['product_category_id']
                          == product_category_id]
    alldata.dropna(axis='rows', subset=[
                   'problem'], inplace=True, ignore_index=True)
    alldata = alldata.reindex(columns=['id', 'problem'])

    # This file holds the results of the quest.
    questdata = pd.read_csv(pathfuncs.DATA_DIR + '/quests/vacuums/dustup.csv')
    questdata.rename(columns={'id_ords': 'id'}, inplace=True)
    questdata = questdata.reindex(columns=['id', 'fault_type'])

    # This file was created by manual review of some records not included in the quest.
    valdata = pd.read_csv(pathfuncs.DATA_DIR + '/quests/vacuums/dustup_validate_en.csv')
    valdata = valdata.reindex(columns=['id', 'fault_type'])

    # Join the datasets.
    jdata = alldata.set_index('id').join(questdata.set_index('id')).join(
        valdata.set_index('id'), lsuffix='_q', rsuffix='_v')

    logger.debug('*** NEW DATA ***')
    data = detect_language(clean_text(
        jdata.loc[(jdata.fault_type_q.isna()) & (jdata.fault_type_v.isna())]))
    data = data.loc[data.language == language]
    data.drop(columns=['fault_type_q','fault_type_v'], inplace=True)
    logger.debug(data)

    logger.debug('*** VAL DATA ***')
    valdata = detect_language(clean_text(
        jdata.loc[(jdata.fault_type_v.notna())]))
    valdata = valdata.loc[valdata.language == language]
    valdata.rename(columns={'fault_type_v': 'fault_type'}, inplace=True)
    valdata.drop(columns='fault_type_q', inplace=True)
    logger.debug(valdata)

    logger.debug('*** QUEST DATA ***')
    questdata = detect_language(clean_text(
        jdata.loc[(jdata.fault_type_q.notna())]))
    questdata = questdata.loc[questdata.language == language]
    questdata.rename(columns={'fault_type_q': 'fault_type'}, inplace=True)
    questdata.drop(columns='fault_type_v', inplace=True)
    logger.debug(questdata)

    return {'questdata': questdata, 'valdata': valdata, 'data': data, }


def clean_text(data, dropna=True):

    # Make sure there is always a space after a period, else sentences won't be split.
    data.replace({'problem': r'(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))'}, {
        'problem': '\\2. \\3'}, regex=True, inplace=True)
    # Remove HTML symbols (&gt; features a lot)
    data.replace(
        {'problem': r'(?i)(&[\w\s]+;)'}, {'problem': ''}, regex=True, inplace=True)
    # Remove weight values (0.5kg, 5kg, 5 kg, .5kg etc.)
    data.replace(
        {'problem': r'(?i)(([0-9]+)?\.?[0-9\s]+kg)'}, {'problem': ''}, regex=True, inplace=True)
    # Remove strange codes often found prefixing `problem` strings.
    data.replace(
        {'problem': r'(?i)^(\W|\d+)([\d|\W]+)?'}, {'problem': ''}, regex=True, inplace=True)
    # Trim whitespace from `problem` strings.
    data['problem'].str.strip()
    if dropna:
        # Drop `problem` values that may be empty after the replacements and trimming.
        data.dropna(subset=['problem'], inplace=True)
    return data


# Use a pre-trained model to detect and set the language.
# This should be more accurate than DeepL's language detection, though model still being refined.
# Requires that `ords_lang_training.py` has created the model object.
def detect_language(data):

    path = pathfuncs.OUT_DIR + '/ords_lang_obj_tfidf_cls.joblib'
    if not pathfuncs.check_path(path):
        print('Model object not found at {}'.format(path))
        data.loc[:, 'language'] = '??'
    else:
        model = load(path)
        data.loc[:, 'language'] = model.predict(data.problem)

    return data


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        self.rx = re.compile('[\W\d_]')

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))]


def get_stopwords():
    stopfile1 = open(pathfuncs.DATA_DIR + '/stopwords-english.txt', "r")
    stopfile2 = open(pathfuncs.DATA_DIR + '/stopwords-english-repair.txt', "r")
    stoplist = stopfile1.read().replace("\n", ' ') + \
        stopfile2.read().replace("\n", ' ')
    stopfile1.close()
    stopfile2.close()
    return stoplist


def do_training(questdata):
    tokenizer = LemmaTokenizer()
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(tokenizer=tokenizer,
         stop_words=tokenizer(get_stopwords()))),
        ('clf', MultinomialNB(force_alpha=True, alpha=0.01)),
    ])
    pipe.fit(questdata.problem, questdata.fault_type)
    dump(pipe, pipefile)
    predictions = pipe.predict(questdata.problem)
    logger.debug('** TRAINING : F1 SCORE: {}'.format(
        metrics.f1_score(questdata.fault_type, predictions, average='macro')))

    questdata.loc[:, 'prediction'] = predictions
    questdata.to_csv(pathfuncs.OUT_DIR +
                '/ords_quest_vacuum_training_results.csv', index=False)

    logger.debug('** TRAINING MISSES **')
    misses = questdata[(questdata['fault_type'] != questdata['prediction'])]
    logger.debug(misses)
    misses.to_csv(pathfuncs.OUT_DIR +
                  '/ords_quest_vacuum_training_misses.csv', index=False)


def do_validation(valdata):

    pipe = load(pipefile)
    predictions = pipe.predict(valdata.problem)
    logger.debug('** VALIDATION : F1 SCORE: {}'.format(
        metrics.f1_score(valdata.fault_type, predictions, average='macro')))
    logger.debug(metrics.classification_report(
        valdata.fault_type, predictions))

    valdata.loc[:, 'prediction'] = predictions
    valdata.to_csv(pathfuncs.OUT_DIR +
                '/ords_quest_vacuum_validation_results.csv', index=False)

    logger.debug('** VALIDATION MISSES **')
    misses = valdata[(valdata['fault_type'] != valdata['prediction'])]
    logger.debug(misses)
    misses.to_csv(pathfuncs.OUT_DIR +
                  '/ords_quest_vacuum_validation_misses.csv', index=False)


def do_test(data):

    pipe = load(pipefile)
    data.loc[:, 'prediction'] = pipe.predict(data.problem)
    data.to_csv(pathfuncs.OUT_DIR +
                '/ords_quest_vacuum_test_results.csv', index=False)


# START

logger = logfuncs.init_logger(__file__)

pipefile = pathfuncs.OUT_DIR + '/ords_quest_vacuum_obj_tfidf_cls.joblib'

datasets = get_datasets(product_category_id=34, language='en')

do_training(datasets['questdata'])

do_validation(datasets['valdata'])

do_test(datasets['data'])
