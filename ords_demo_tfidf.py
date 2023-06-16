#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
logger = logfuncs.init_logger(__file__)

# Demonstration of extracting vocabulary, features and "bag of words" using TfidfVectorizer.

# Read the data file as type string with na values set to empty string.
df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                 keep_default_na=False, na_values="")
# Filter for records from the UK/USA as they will mostly be in English (see 'stopwords').
df = df[df['country'].isin(['GBR', 'USA'])]
# Filter for decent length problem strings.
dfx = df[(df['problem'].apply(lambda s: len(str(s)) > 64))]

categories = pd.read_csv(pathfuncs.ORDS_DIR +
                         '/{}.csv'.format(envfuncs.get_var('ORDS_CATS')))


def get_item_types(category):

    sr_res = df.loc[df.product_category ==
                    category]['partner_product_category'].reset_index(drop=True).squeeze()
    np_res = sr_res.str.split('~').str.get(1).str.strip().dropna().unique()
    logger.debug(np_res)
    return np_res


def get_problem_text(category):

    return dfx.loc[df.product_category == category]['problem'].reset_index(drop=True).squeeze().dropna().unique()


tv = TfidfVectorizer(norm=None)
cv = CountVectorizer()

def fit_item_types():

    logger.debug('*** ITEM TYPE TfidfVectorizer ***')
    # Using derived `item_type` values.
    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        logger.debug('**** {} ****'.format(category))
        strings = get_item_types(category)

        tv_fit = tv.fit_transform(strings).toarray()
        cv_fit = cv.fit_transform(strings).toarray()

        logger.debug('** TV vocabulary **')
        logger.debug(tv.vocabulary_)
        logger.debug('** CV vocabulary **')
        logger.debug(cv.vocabulary_)

        logger.debug('** TV feature names **')
        logger.debug(tv.get_feature_names_out())
        logger.debug('** CV feature names **')
        logger.debug(cv.get_feature_names_out())

        # logger.debug('** TV bag of words **')
        # logger.debug(tv_fit)
        # logger.debug('** CV bag of words **')
        # logger.debug(cv_fit)

def fit_problem_text():

    logger.debug('*** PROBLEM ***')

    logger.debug('*** TfidfVectorizer ***')
    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        logger.debug('**** {} ****'.format(category))
        strings = get_problem_text(category)

        tv_fit = tv.fit_transform(strings).toarray()
        cv_fit = cv.fit_transform(strings).toarray()

        foo = tv.vocabulary_
        bar = cv.vocabulary_
        if (foo != bar):
            logger.debug('** DIFF vocabulary **')
        logger.debug('** TV vocabulary **')
        logger.debug(tv.vocabulary_)
        logger.debug('** CV vocabulary **')
        logger.debug(cv.vocabulary_)

        foo = tv.get_feature_names_out()
        bar = cv.get_feature_names_out()
        if ((foo != bar).all()):
            logger.debug('** DIFF feature names **')
        logger.debug('** TV feature names **')
        logger.debug(tv.get_feature_names_out())
        logger.debug('** CV feature names **')
        logger.debug(cv.get_feature_names_out())

        # logger.debug('** TV bag of words **')
        # logger.debug(tv_fit)
        # logger.debug('** CV bag of words **')
        # logger.debug(cv_fit)

fit_item_types()
fit_problem_text()