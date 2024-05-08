#!/usr/bin/env python3


# Demonstration of extracting vocabulary, features and "bag of words" using TfidfVectorizer.

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer


def get_item_types(category):

    sr = (
        df.loc[df.product_category == category]["partner_product_category"]
        .reset_index(drop=True)
        .squeeze()
    )
    if sr.empty:
        logger.debug("No records for catgegory")
        return sr

    return sr.str.rsplit("~").str.get(0).str.strip().dropna().unique()


def get_problem_text(category):

    sr = df.loc[df.product_category == category]["problem"].dropna()
    if sr.empty:
        logger.debug("No records for catgegory")

    return sr


def fit_item_types():

    logger.debug("*** ITEM TYPE TfidfVectorizer ***")
    # Using derived `item_type` values.
    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        logger.debug("**** {} ****".format(category))
        strings = get_item_types(category)
        if not strings.any():
            continue

        tv_fit = tv.fit_transform(strings).toarray()
        cv_fit = cv.fit_transform(strings).toarray()

        logger.debug("** TV vocabulary **")
        logger.debug(tv.vocabulary_)
        logger.debug("** CV vocabulary **")
        logger.debug(cv.vocabulary_)

        logger.debug("** TV feature names **")
        logger.debug(tv.get_feature_names_out())
        logger.debug("** CV feature names **")
        logger.debug(cv.get_feature_names_out())

        # logger.debug('** TV bag of words **')
        # logger.debug(tv_fit)
        # logger.debug('** CV bag of words **')
        # logger.debug(cv_fit)


def fit_problem_text():

    logger.debug("*** PROBLEM ***")

    logger.debug("*** TfidfVectorizer ***")
    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        logger.debug("**** {} ****".format(category))
        strings = get_problem_text(category)
        if not strings.any():
            continue

        tv_fit = tv.fit_transform(strings).toarray()
        cv_fit = cv.fit_transform(strings).toarray()

        foo = tv.vocabulary_
        bar = cv.vocabulary_
        if foo != bar:
            logger.debug("** DIFF vocabulary **")
        logger.debug("** TV vocabulary **")
        logger.debug(tv.vocabulary_)
        logger.debug("** CV vocabulary **")
        logger.debug(cv.vocabulary_)

        logger.debug("** TV stop words **")
        logger.debug(tv.get_stop_words())
        logger.debug("** CV stop words **")
        logger.debug(cv.get_stop_words())

        foo = tv.get_feature_names_out()
        bar = cv.get_feature_names_out()
        if (foo != bar).all():
            logger.debug("** DIFF feature names **")
        logger.debug("** TV feature names **")
        logger.debug(tv.get_feature_names_out())
        logger.debug("** CV feature names **")
        logger.debug(cv.get_feature_names_out())

        # logger.debug('** TV bag of words **')
        # logger.debug(tv_fit)
        # logger.debug('** CV bag of words **')
        # logger.debug(cv_fit)


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    # Read the data file as type string with na values set to empty string.
    df = pd.read_csv(
        pathfuncs.path_to_ords_csv(), dtype=str, keep_default_na=False, na_values=""
    )
    # Filter for small subset with English language text.
    df = df[df["country"].isin(["USA"])]

    categories = pd.read_csv(
        pathfuncs.ORDS_DIR + "/{}.csv".format(envfuncs.get_var("ORDS_CATS"))
    )

    tv = TfidfVectorizer()
    cv = CountVectorizer()

    fit_item_types()
    fit_problem_text()
