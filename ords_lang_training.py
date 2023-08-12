#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
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

** Validation stats (MultinomialNB)

prediction  agree  percent
    total   19552       98
        de  12815      100
        en   3335       91
        es      3      100
        fr    345       92
        nl   3054       97

* Comparisons:

Total predictions	69,082

** Google
[Sheets 'DETECTLANGUAGE' function](https://support.google.com/docs/answer/3093278?hl=en-GB)
Agree	    66,901	98.37%
Disagree	1,111	1.63%
Don't know	10	    0.01%

** Python
[Nakatani Shuyo's language-detection library](https://github.com/Mimino666/langdetect)
'This library is a direct port of Google's language-detection library from Java to Python. All the classes and methods are unchanged, so for more information see the project's website or wiki.'
[Detect an Unknown Language using Python](https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/)
Agree	    54,326	79.88%
Disagree	13,685	20.12%
Don't know	5	    0.01%

** OpenRefine
[Language Detection Library for Java](https://github.com/optimaize/language-detector#71-built-in-language-profiles)
'This software does not work as well when the input text to analyze is short, or unclean.'
'If you are looking for a language detector / language guesser library in Java, this seems to be the best open source library you can get at this time.'
Note: Takes hours to run!
Agree	    42,171	62.00%
Disagree	2,200	3.23%
Don't know	23,642	34.76%

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
    dfx['agree'] = dfx.language_known == dfx.prediction
    dfx.rename(columns={'problem_x': 'problem',
               'problem_y': 'cleaned', }, inplace=True)
    dfx.drop(['id_ords'], axis=1, inplace=True)
    outfile = format_path('ords_lang_checks_detection')
    dfx.to_csv(outfile, index=False)
    print("Annotated results written to {}".format(outfile))

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
    # df['language_known'] = df['language_known'].str.lower()
    df = df.reindex(columns=['id_ords', 'language_known', 'problem'])
    # df.rename(columns={'language_known': 'deepl'}, inplace=True)
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


# Merge the language columns from the translations table into a single `problem` text field
# and label each row with the known language.
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
        "da": "danish"
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
def get_alpha(data, labels, vects, search=False):
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

    # Get the alpha value.
    # Use search=True to find a good value, or False for default.
    # If a better value than default is found, replace default with it.
    alpha = get_alpha(column, labels, feature_vects, search=False)

    # Other classifiers are available!
    # https://scikit-learn.org/stable/modules/naive_bayes.html
    # Tuning different classifiers could sway results.

    # Validation test  MultinomialNB' F1 SCORE: 0.6970076612719212
    # Classed '??' as English.
    classifier = MultinomialNB(
        force_alpha=True, alpha=alpha)

    # Validation test  ComplementNB' F1 SCORE: 0.5480281790194357
    # Classed '??' as Danish.
    # from sklearn.naive_bayes import ComplementNB
    # classifier = ComplementNB(
    #     force_alpha=True, alpha=alpha)

    logger.debug('** TRAIN : vectorizer ~ shape **')
    logger.debug(feature_vects.shape)
    logger.debug('** TRAIN : vectorizer ~ feature names **')
    logger.debug(vectorizer.get_feature_names_out())

    # Fit the data.
    classifier.fit(feature_vects, labels)
    logger.debug('** TRAIN : classifier: params **')
    logger.debug(classifier.get_params())

    # Get predictions on own features.
    predictions = classifier.predict(feature_vects)
    logger.debug('** TRAIN : classifier: F1 SCORE: {}'.format(
        metrics.f1_score(labels, predictions, average='macro')))
    logger.debug(predictions)

    # Save the classifier and vectoriser objects for re-use.
    dump(classifier, clsfile)
    dump(vectorizer, tdffile)
    # Create and save a pipeline for re-use.
    pipe = Pipeline([
        ('tfidf', vectorizer),
        ('clf', classifier),
    ])
    pipe.fit(column, labels)
    dump(pipe, pipefile)

    # Save predictions to 'out' directory in csv format.
    data.loc[:, 'prediction'] = predictions
    data.to_csv(format_path('ords_lang_results_training'), index=False)

    # Save prediction misses.
    misses = data[(data['language'] != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_lang_misses_training'), index=False)


# Validate the model with either pipeline or vect/class objects.
# Try each to ensure object integrity.
def do_validation(data, pipeline=False):

    data.dropna(axis='rows', subset=[
        'problem'], inplace=True, ignore_index=True)
    column = data.problem
    labels = data.language_known
    logger.debug('** VALIDATE : using pipeline - {}'.format(pipeline))
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

    logger.debug('** VALIDATE : classifier: F1 SCORE: {}'.format(
        metrics.f1_score(labels, predictions, average='macro')))
    logger.debug(metrics.classification_report(
        labels, predictions))

    # Predictions output for inspection.
    data.loc[:, 'prediction'] = predictions
    data.to_csv(format_path('ords_lang_results_validation'), index=False)

    # Prediction misses for inspection.
    misses = data[(data.language_known != data['prediction'])]
    logger.debug(misses)
    misses.to_csv(format_path('ords_lang_misses_validation'), index=False)


# Use model on untrained data, with either pipeline or vect/class objects.
def do_detection(data, pipeline=False):

    data.dropna(axis='rows', subset=[
        'problem'], inplace=True, ignore_index=True)
    column = data.problem
    logger.debug('** DETECT : using pipeline - {}'.format(pipeline))
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
    data.loc[:, 'prediction'] = predictions
    data = data.reindex(columns=['id', 'problem', 'prediction'])
    data.to_csv(format_path('ords_lang_results_detection'), index=False)
    return data


def format_path(filename, ext='csv'):
    return '{}/{}.{}'.format(pathfuncs.OUT_DIR, filename, ext)


# START

# Path to the model objects for dump/load.
clsfile = format_path('ords_lang_obj_cls', 'joblib')
tdffile = format_path('ords_lang_obj_tdif', 'joblib')
pipefile = format_path('ords_lang_obj_tfidf_cls', 'joblib')

training_data = get_training_data(sample=1, min=5, max=255)
logger.debug('*** TRAINING DATA ***')
logger.debug(training_data)
training_data.to_csv(format_path('ords_lang_data_training'), index=False)
do_training(data=training_data,
            stopwords=get_stopwords())

validation_data = get_validation_data()
logger.debug('*** VALIDATION DATA ***')
logger.debug(validation_data)
validation_data.to_csv(format_path('ords_lang_data_validation'), index=False)
do_validation(data=validation_data, pipeline=True)

# Read the entire ORDS export.
all_data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
predictions = do_detection(data=all_data, pipeline=True)

# Check and summarise results.
annotate_results(dfv=validation_data, dfx=predictions)
