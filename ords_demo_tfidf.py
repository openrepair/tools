#!/usr/bin/env python3

# Demonstration of extracting vocabulary, features and "bag of words" using TfidfVectorizer.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import polars as pl
from funcs import *


# Using English language records (assumed by country).
def get_data():
    return ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")).filter(
        pl.col("country").is_in(["USA"]),
        pl.col("problem").str.len_chars() > 24,
    )


def get_problem_text(data, category):

    return list(
        data.filter(
            pl.col("product_category") == category,
        ).select(
            pl.col(
                "problem",
            )
        )["problem"]
    )


# Split the partner_product_category string.
def get_products(data, category):

    return list(
        ordsfuncs.extract_products(
            data.filter(
                pl.col("product_category") == category,
            )
        )
        .select(pl.col("product"))
        .drop_nulls()
        .unique()["product"]
    )


# Using derived `item_type` values.
def fit_products(data):

    logger.debug("*** PRODUCT TfidfVectorizer ***")
    categories = ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS"))
    for id, category in categories.iter_rows():
        logger.debug("**** {} ****".format(data, category))
        strings = get_products(data, category)
        if len(strings) == 0:
            continue

        tv = TfidfVectorizer()
        cv = CountVectorizer()

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


def fit_problem_text(data):

    logger.debug("*** PROBLEM ***")
    categories = ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS"))
    logger.debug("*** TfidfVectorizer ***")
    for id, category in categories.iter_rows():
        logger.debug("**** {} ****".format(category))
        # strings = get_problem_text(data, category)

        strings = list(
            data.filter(
                pl.col("product_category") == category,
            ).select(
                pl.col(
                    "problem",
                )
            )["problem"]
        )

        if len(strings) == 0:
            continue

        tv = TfidfVectorizer()
        cv = CountVectorizer()

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

    logger = cfg.init_logger(__file__)

    data = get_data()
    fit_products(data)
    fit_problem_text(data)
