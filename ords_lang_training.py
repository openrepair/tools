#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn import model_selection
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from joblib import dump
from joblib import load

logger = logfuncs.init_logger('ords_lang_training')

# An attempt at using the DeepL translated problem text to train an NLP model using scikit-learn.
# See dat/ords_problem_translations.csv and ords_deepl_setup.py

"""
Total predictions	86,341

* Comparisons

** Google
[Sheets 'DETECTLANGUAGE' function](https://support.google.com/docs/answer/3093278?hl=en-GB)
Agree	    82,573	95.64%
Disagree	3,767	4.36%
Don't know	148	    0.17%

** Python
[Nakatani Shuyo's language-detection library](https://github.com/Mimino666/langdetect)
'This library is a direct port of Google's language-detection library from Java to Python. All the classes and methods are unchanged, so for more information see the project's website or wiki.'
[Detect an Unknown Language using Python](https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/)
Agree	    67,785	78.51%
Disagree	18,523	21.45%
Don't know	91	    0.11%

** OpenRefine
[Language Detection Library for Java](https://github.com/optimaize/language-detector#71-built-in-language-profiles)
'This software does not work as well when the input text to analyze is short, or unclean.'
'If you are looking for a language detector / language guesser library in Java, this seems to be the best open source library you can get at this time.'
Note: Takes hours to run!
Agree	    53,350	61.79%
Disagree	3,866	4.48%
Don't know	29,125	33.73%

** OpenNLP
[Documentation](https://opennlp.apache.org/docs/2.2.0/manual/opennlp.html)
'The OpenNLP Language Detector classifies a document in ISO-639-3 languages according to the model capabilities. A model can be trained with Maxent, Perceptron or Naive Bayes algorithms.'
Requires a pre-trained model, several are provided.
Not tested due to issues setting it up.
"""


# Output results with added training data details.
# Output training data stats.
def annotate_results(dft, dfx):

    # Don't need these and makes the annotation merge easier.
    dft.drop('prediction', axis=1, inplace=True)
    dft['result_type'] = 'trained'
    dfx = dfx.merge(dft, how='outer', left_on='problem', right_on='problem')
    dfx.fillna({"result_type": 'untrained'}, inplace=True)
    dfx['agree'] = dfx.lang_known == dfx.prediction
    dfx.to_csv(pathfuncs.OUT_DIR +
               '/ords_lang_test_checks.csv', index=False)
    print("Annotated results written to {}".format(
        pathfuncs.OUT_DIR + '/ords_lang_test_checks.csv'))

    # stats

    dfs = dfx.loc[(dfx.result_type == 'trained')]
    gbs = dfs.groupby('prediction')

    dfa = dfs.loc[dfs.agree == True]
    gba = dfa.groupby('prediction')

    d = {'prediction': ['Total'], 'agree': [dfa['id'].count()], 'percent': [
        dfa['id'].count() / dfs['id'].count() * 100]}
    df = pd.DataFrame(data=d)

    for name, group in gba:
        d = {'prediction': [name], 'agree': [group['id'].count()], 'percent': [
            group['id'].count() / gbs.get_group(name)['id'].count() * 100]}
        df = pd.concat([df, pd.DataFrame(data=d)])
    # logger.debug(df)
    df.to_csv(pathfuncs.OUT_DIR +
              '/ords_lang_test_stats.csv', index=False)
    print("Result stats written to {}".format(
        pathfuncs.OUT_DIR + '/ords_lang_test_stats.csv'))


# Merge the language columns from the translations table into a single problem text field and label each row with the known language.
def get_training_data():

    data = pd.read_csv(pathfuncs.DATA_DIR + '/ords_problem_translations.csv')
    logger.debug('*** RAW DATA ***')
    logger.debug(data)
    langs = ['en', 'de', 'nl', 'fr', 'it', 'es']
    dfr = pd.DataFrame(columns=['problem', 'lang_known'])
    for lang in langs:
        dft = pd.DataFrame(data=data[lang].unique(),
                           columns=['problem']).dropna()
        dft['lang_known'] = lang
        logger.debug('*** {} DATA ***'.format(lang))
        logger.debug(dft)
        dfr = pd.concat([dfr, dft])
    logger.debug('*** COMPILED DATA ***')
    logger.debug(dfr)
    dfr.to_csv(format_path('ords_lang_training_data'), index=False)
    return dfr


# So far all training data returns an alpha of 0.
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
        msg = '** TRAIN: classifier best alpha value(s): {}'.format(
            multinomial_nb_grid.best_params_)
        logger.debug(msg)
        print(msg)
        return multinomial_nb_grid.best_params_['alpha']
    else:
        return 0


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        # Ignore all punctuation except apostrophes.
        self.rx = re.compile("[^'^\s\w]+|[\d]")

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))]


def get_stopwords():
    stopfile = open(pathfuncs.DATA_DIR +
                    '/ords_lang_training_stopwords.txt', "r")
    stoplist = list(stopfile.read().replace("\n", ' '))
    stopfile.close()
    return stoplist


def do_training(data, tokenizer=False, stopwords=False):

    column = data.problem
    labels = data.lang_known

    vectorizer = TfidfVectorizer()

    if tokenizer != False:
        tokenizer = LemmaTokenizer()
        vectorizer.set_params(tokenizer=tokenizer)

    if stopwords != False:
        vectorizer.set_params(stop_words=stopwords)

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
    data.to_csv(format_path('ords_lang_training_results'), index=False)

    # Save prediction misses.
    misses = data[(data['lang_known'] != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_lang_training_misses'), index=False)


def do_test(data):

    data.dropna(axis='rows', subset=[
        'problem'], inplace=True, ignore_index=True)

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
    data.to_csv(format_path('ords_lang_test_results'), index=False)
    return data


def format_path(filename, ext='csv'):
    return '{}/{}.{}'.format(pathfuncs.OUT_DIR, filename, ext)


# START

# Path to the classifier and vectoriser objects for dump/load.
clsfile = format_path('ords_lang_obj_nbcl', 'joblib')
tdffile = format_path('ords_lang_obj_tdif', 'joblib')

training_data = get_training_data()
do_training(data=training_data,
            stopwords=get_stopwords(), tokenizer=True)

# Read the entire ORDS export.
all_data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
predictions = do_test(data=all_data)

annotate_results(dft=training_data, dfx=predictions)
