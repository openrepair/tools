#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
logger = logfuncs.init_logger(__file__)

"""
Attempts to extract a vocabulary from the data for each ORDS category
from either the problem text or by deriving the `item_type`.
ToDo:
    Describe use-cases, e.g. "find fault types" and "verify category".
    Build corpus-specific stopword list for each context
        e.g. for `problem` - "broke", "broken", "fail", "failed", etc.
        e.g. for `item_type` - "electric", "household", "equipment", "device", etc.
"""


# Read the data file as type string with na values set to empty string.
df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                 keep_default_na=False, na_values="")
# Filter for small subset with English language text.
df = df[df['country'].isin(
    ['USA', 'GBR', 'AUS', 'IRL', 'ISL', 'JEY', 'NOR', 'NZL', 'SWE'])]

categories = pd.read_csv(pathfuncs.ORDS_DIR +
                         '/{}.csv'.format(envfuncs.get_var('ORDS_CATS')))


# This can leave a number of 2-char words in the vocabulary but some are useful e.g. "tv", "cd".
# Numbers may be useful for some purposes, e.g. "mp3", "ps1"
class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        # Remove numbers and punctuation.
        self.rx = re.compile('[\W\d_]')

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))]


tokenizer = LemmaTokenizer()

# [Using stop words](https://scikit-learn.org/stable/modules/feature_extraction.html#stop-words)
# [Stop Word Lists in Free Open-source Software Packages](https://aclanthology.org/W18-2502/)
# [Stopword Lists for 19 Languages](https://www.kaggle.com/datasets/rtatman/stopword-lists-for-19-languages)
stopfile = open(pathfuncs.DATA_DIR + '/stopwords-english.txt', "r")
# Use same tokenizer on stopwords as used in the vectorizer.
stop_tokens = tokenizer(stopfile.read().replace("\n", ' '))
stopfile.close()

tv = TfidfVectorizer(stop_words=stop_tokens, tokenizer=tokenizer)
logger.debug('*** STOPWORDS ***')
logger.debug(tv.get_stop_words())


def get_item_types(category):

    sr = df.loc[df.product_category ==
                category]['partner_product_category'].reset_index(drop=True).squeeze()
    if sr.empty:
        logger.debug('No records for catgegory')
        return sr

    return sr.str.rsplit('~').str.get(0).str.strip().dropna().unique()


def get_problem_text(category):

    sr = df.loc[df.product_category == category]['problem'].dropna()
    if sr.empty:
        logger.debug('No records for catgegory')

    return sr


# Using `item_type` values derived from the `partner_product_category` column.
# The format of `partner_product_category` values depends on how many category levels existed for each record.
# Format when 2 category levels : [partner lvl-1 category] ~ [partner lvl-2 category]
# Format when either lvl-1 or lvl-2 category: [partner lvl-n category]
def fit_item_types():

    logger.debug('*** ITEM TYPE ***')
    dfx = pd.DataFrame()
    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        logger.debug('**** {} ****'.format(category))
        strings = get_item_types(category)
        if not strings.any():
            continue

        tv.fit_transform(strings)

        logger.debug('** Vocabulary **')
        logger.debug(tv.vocabulary_)

        dfc = pd.DataFrame({'category': category, 'term': tv.vocabulary_.keys(
        ), 'idx': tv.vocabulary_.values()})
        dfx = pd.concat([dfx, dfc])

    path = pathfuncs.OUT_DIR + '/ords_vocabulary_itemtype.csv'
    dfx.to_csv(path, index=False)

    dfs = dfx.groupby(
        ['term']).size().reset_index(name='records')
    dfs.sort_values(by=['records'],
                      ascending=False, inplace=True, ignore_index=True)
    path = pathfuncs.OUT_DIR + '/ords_vocabulary_itemtype_freq.csv'
    dfs.to_csv(path, index=False)


def fit_problem_text():

    logger.debug('*** PROBLEM ***')
    dfx = pd.DataFrame()
    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        logger.debug('**** {} ****'.format(category))
        strings = get_problem_text(category)
        if not strings.any():
            continue

        tv.fit_transform(strings)

        logger.debug('** Vocabulary **')
        logger.debug(tv.vocabulary_)

        dfc = pd.DataFrame({'category': category, 'term': tv.vocabulary_.keys(
        ), 'idx': tv.vocabulary_.values()})
        dfx = pd.concat([dfx, dfc])

    path = pathfuncs.OUT_DIR + '/ords_vocabulary_problem.csv'
    dfx.to_csv(path, index=False)

    dfs = dfx.groupby(
        ['term']).size().reset_index(name='records')
    dfs.sort_values(by=['records'],
                      ascending=False, inplace=True, ignore_index=True)
    path = pathfuncs.OUT_DIR + '/ords_vocabulary_problem_freq.csv'
    dfs.to_csv(path, index=False)


fit_item_types()
fit_problem_text()
