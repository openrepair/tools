#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn import model_selection
from nltk import tokenize
from joblib import dump
from joblib import load

logger = logfuncs.init_logger(__file__)

# An attempt at using the DeepL translated problem text to train an NLP model using scikit-learn.
# See dat/ords_problem_translations.csv and ords_deepl_1setup.py

"""
WORK IN PROGRESS!
TO DO:
    Translate Danish text

** DeepL (validation)

  prediction  agree  percent
0      total  18137       96
1         de  12152       97
2         en   2582       89
3         es      3      100
4         fr    345       92
5         nl   3055       97

* Comparisons:

Total predictions	69,082

** Google
[Sheets 'DETECTLANGUAGE' function](https://support.google.com/docs/answer/3093278?hl=en-GB)
Agree	    67,955	98.37%
Disagree	1,126	1.63%
Don't know	10	    0.01%

** Python
[Nakatani Shuyo's language-detection library](https://github.com/Mimino666/langdetect)
'This library is a direct port of Google's language-detection library from Java to Python. All the classes and methods are unchanged, so for more information see the project's website or wiki.'
[Detect an Unknown Language using Python](https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/)
Agree	    55,305	80.06%
Disagree	13,775	19.94%
Don't know	5	    0.01%

** OpenRefine
[Language Detection Library for Java](https://github.com/optimaize/language-detector#71-built-in-language-profiles)
'This software does not work as well when the input text to analyze is short, or unclean.'
'If you are looking for a language detector / language guesser library in Java, this seems to be the best open source library you can get at this time.'
Note: Takes hours to run!
Agree	    43,075	62.35%
Disagree	2,209	3.20%
Don't know	23,798	34.45%

** OpenNLP
[Documentation](https://opennlp.apache.org/docs/2.2.0/manual/opennlp.html)
'The OpenNLP Language Detector classifies a document in ISO-639-3 languages according to the model capabilities. A model can be trained with Maxent, Perceptron or Naive Bayes algorithms.'
Requires a pre-trained model, several are provided.
Not tested due to issues setting it up.
"""


# Output results with added validation data details.
# Log validation stats.
def annotate_results(dfv, dfx):

    # Don't need these and makes the annotation merge easier.
    dfv.drop('prediction', axis=1, inplace=True)
    dfv['result_type'] = 'trained'
    dfx = dfx.merge(dfv, how='outer', left_on='id', right_on='id_ords')
    dfx.dropna(subset=['id'], inplace=True)
    dfx.fillna({"result_type": 'untrained'}, inplace=True)
    dfx['agree'] = dfx.deepl == dfx.prediction
    dfx.rename(columns={'problem_x': 'problem',
               'problem_y': 'cleaned', }, inplace=True)
    dfx.drop(['id_ords'], axis=1, inplace=True)
    dfx.to_csv(pathfuncs.OUT_DIR +
               '/ords_lang_checks_detection.csv', index=False)
    print("Annotated results written to {}".format(
        pathfuncs.OUT_DIR + '/ords_lang_checks_detection.csv'))

    # stats

    dfs = dfx.loc[(dfx.result_type == 'trained')]
    gbs = dfs.groupby('prediction')

    dfa = dfs.loc[dfs.agree == True]
    gba = dfa.groupby('prediction')

    d = {'prediction': ['total'], 'agree': [dfa['id'].count()], 'percent': [
        round(dfa['id'].count() / dfs['id'].count() * 100)]}
    df = pd.DataFrame(data=d)

    for name, group in gba:
        d = {'prediction': [name], 'agree': [group['id'].count()], 'percent': [
            round(group['id'].count() / gbs.get_group(name)['id'].count() * 100)]}
        df = pd.concat([df, pd.DataFrame(data=d)])
    logger.debug('Validation stats')
    logger.debug(df)


# Clean all of the `problem` fields from the ORDS translations file.
def get_validation_data():

    df = pd.read_csv(pathfuncs.DATA_DIR +
                     '/ords_problem_translations.csv', dtype=str)
    df['language_detected'] = df['language_detected'].str.lower()
    df = df.reindex(columns=['id_ords', 'language_detected', 'problem'])
    df.rename(columns={'language_detected': 'deepl'}, inplace=True)
    df = clean_text(df, dedupe=False, dropna=False)
    return df


def clean_text(data, dedupe=True, dropna=True):

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
    if dedupe:
        # Dedupe the `problem` values.
        data.drop_duplicates(subset=['problem'], inplace=True)
    return data


# Merge the language columns from the translations table into a single `problem` text field and label each row with the known language.
# Then clean and split the `problem` text into sentences.
# This is used for training.
def get_training_data(sample=1, min=2, max=255):

    # Map the ISO lang codes to the names of the nltk language models.
    langs = {
        "en": "english",
        "de": "german",
        "nl": "dutch",
        "fr": "french",
        "it": "italian",
        "es": "spanish",
    }
    # Read input DataFrame.
    df_in = pd.read_csv(pathfuncs.DATA_DIR + '/ords_problem_translations.csv')
    # Create output DataFrame, naming column `sentence` to remind that it is not the entire `problem` string.
    df_out = pd.DataFrame(columns=['sentence', 'language'])
    for lang in langs.keys():
        # Filter for non-empty unique strings in the `problem` column.
        df_tmp = pd.DataFrame(data=df_in[lang].unique(),
                              columns=['problem']).dropna()
        df_tmp = clean_text(df_tmp)
        # Create a new language-specific list for the sentences.
        langlist = []
        for i, row in df_tmp.iterrows():
            try:
                # Split the `problem` string into sentences.
                sentences = tokenize.sent_tokenize(
                    row.problem, language=langs[lang])
                # Add the sentences to the list for this language.
                langlist.extend(sentences)
            except Exception as error:
                print(error)

        # Remove duplicates from the langlist and convert to DataFrame.
        df_lang = pd.DataFrame(data=list(set(langlist)), columns=["sentence"])
        # Remove multiple punctuation characters (???, --, ..., etc.)
        df_lang.replace({'sentence': r'(?i)([\W]{2,})'}, {
                        'sentence': ' '}, regex=True, inplace=True)
        # Trim whitespace from `sentence` strings (again).
        df_lang['sentence'].str.strip()
        # Add the ISO code to the DataFrame for this language.
        df_lang['language'] = lang
        # Add the language DataFrame to the output DataFrame.
        df_out = pd.concat([df_out, df_lang])

    # Finally, reduce and sample the results.
    df_out = df_out[(df_out['sentence'].apply(lambda s: len(
        str(s)) in range(min, max+1)))].sample(frac=sample)
    return df_out


# Use this to check for best value and set it as default
# Don't use every time, it slows down execution considerably.
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
        return 0.1


def get_stopwords():
    stopfile = open(pathfuncs.DATA_DIR +
                    '/ords_lang_training_stopwords.txt', "r")
    stoplist = list(stopfile.read().replace("\n", ' '))
    stopfile.close()
    return stoplist


def do_training(data, stopwords=False):

    column = data.sentence
    labels = data.language

    vectorizer = TfidfVectorizer()

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
    data.to_csv(format_path('ords_lang_results_training'), index=False)

    # Save prediction misses.
    misses = data[(data['language'] != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_lang_misses_training'), index=False)


def do_validation(data):

    column = data.problem
    labels = data.deepl

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
    data.to_csv(format_path('ords_lang_results_validation'), index=False)

    # Prediction misses for inspection.
    misses = data[(data['deepl'] != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_lang_misses_validation'), index=False)


def do_detection(data):

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
    data = data.reindex(columns=['id', 'problem', 'prediction'])
    data.to_csv(format_path('ords_lang_results_detection'), index=False)
    return data


def format_path(filename, ext='csv'):
    return '{}/{}.{}'.format(pathfuncs.OUT_DIR, filename, ext)


# START

# Path to the classifier and vectoriser objects for dump/load.
clsfile = format_path('ords_lang_obj_nbcl', 'joblib')
tdffile = format_path('ords_lang_obj_tdif', 'joblib')

training_data = get_training_data(sample=1, min=5, max=255)
logger.debug('*** TRAINING DATA ***')
logger.debug(training_data)
training_data.to_csv(pathfuncs.OUT_DIR +
                     '/ords_lang_data_training.csv', index=False)
do_training(data=training_data,
            stopwords=get_stopwords())

validation_data = get_validation_data()
logger.debug('*** VALIDATION DATA ***')
logger.debug(validation_data)
validation_data.to_csv(pathfuncs.OUT_DIR +
                       '/ords_lang_data_validation.csv', index=False)
do_validation(data=validation_data)

# Read the entire ORDS export.
all_data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
predictions = do_detection(data=all_data)

# For checking validation results
annotate_results(dfv=validation_data, dfx=predictions)
