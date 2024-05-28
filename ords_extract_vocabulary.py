#!/usr/bin/env python3

# Attempts to extract a vocabulary from the data for each ORDS category
# from either the problem text or by deriving the `product`.
# ToDo: Describe vocabulary use-cases, e.g. "find fault types" and "verify category".

import re
import polars as pl
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from funcs import *


# This can leave a number of 2-char words in the vocabulary but some are useful e.g. "tv", "cd", "pc".
# Numbers may be useful for some purposes, e.g. "mp3", "ps1"
class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        # Remove numbers and punctuation.
        self.rx = re.compile("[\W\d_]")

    def __call__(self, doc):
        return [
            self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))
        ]


def get_vectorizer():
    tokenizer = LemmaTokenizer()
    # [Using stop words](https://scikit-learn.org/stable/modules/feature_extraction.html#stop-words)
    # [Stop Word Lists in Free Open-source Software Packages](https://aclanthology.org/W18-2502/)
    # [Stopword Lists for 19 Languages](https://www.kaggle.com/datasets/rtatman/stopword-lists-for-19-languages)
    stopfile1 = open(cfg.DATA_DIR + "/stopwords-english.txt", "r")
    # ORDS corpus custom stopwords.
    stopfile2 = open(cfg.DATA_DIR + "/stopwords-english-repair.txt", "r")
    stoplist = stopfile1.read().replace("\n", " ") + stopfile2.read().replace("\n", " ")
    stopfile1.close()
    stopfile2.close()
    # Use same tokenizer on stopwords as used in the vectorizer.
    stop_tokens = tokenizer(stoplist)

    tv = TfidfVectorizer(stop_words=stop_tokens, tokenizer=tokenizer)
    logger.debug("*** STOPWORDS ***")
    logger.debug(tv.get_stop_words())
    return tv


# Split the partner_product_category string.
# Using English language records (assumed by country).
def get_products(category):

    df = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")).filter(
        pl.col("product_category") == category,
        pl.col("country").is_in(["USA", "GBR", "AUS", "IRL", "JEY", "NZL"]),
    )
    return list(
        ordsfuncs.extract_products(df)
        .select(pl.col("product"))
        .drop_nulls()
        .unique()["product"]
    )


def get_problem_text(category):

    df = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA")).filter(
        pl.col("product_category") == category,
        pl.col("country").is_in(["USA", "GBR", "AUS", "IRL", "JEY", "NZL"]),
    )
    return list(df.select(pl.col("problem")).drop_nulls().unique()["problem"])


# Using `product` values derived from the `partner_product_category` column.
# The format of `partner_product_category` values depends on how many category levels existed for each record.
# Format when 2 category levels : [partner lvl-1 category] ~ [partner lvl-2 category]
# Format when either lvl-1 or lvl-2 category: [partner lvl-n category]
def fit_products():

    logger.debug("*** ITEM TYPE ***")
    # Changes to the ORDS categories will require updates to the regexes.
    categories = ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS"))
    tv = get_vectorizer()

    df_out = pl.DataFrame(
        schema={
            "product_category": pl.String,
            "term": pl.String,
            "idx": pl.Int64,
        },
    )
    for id, category in categories.iter_rows():
        logger.debug("**** {} ****".format(category))
        strings = get_products(category)
        if len(strings) == 0:
            continue

        tv.fit_transform(strings)

        logger.debug("** Vocabulary **")
        logger.debug(tv.vocabulary_)

        df_tmp = pl.DataFrame(
            data={
                "product_category": category,
                "term": tv.vocabulary_.keys(),
                "idx": tv.vocabulary_.values(),
            }
        )
        logger.debug(df_tmp.height)
        df_out.extend(df_tmp)
        logger.debug(df_out.height)

    df_out.write_csv(cfg.OUT_DIR + "/ords_vocabulary_products.csv")

    df_out.group_by(["term"]).len(name="records").sort(
        "records", descending=True
    ).write_csv(cfg.OUT_DIR + "/ords_vocabulary_products_freq.csv")


def fit_problem_text():

    logger.debug("*** PROBLEM ***")
    categories = ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS"))
    tv = get_vectorizer()
    df_out = pl.DataFrame(
        schema={
            "product_category": pl.String,
            "term": pl.String,
            "idx": pl.Int64,
        },
    )
    for id, category in categories.iter_rows():
        logger.debug("**** {} ****".format(category))
        strings = get_problem_text(category)
        if len(strings) == 0:
            continue

        tv.fit_transform(strings)

        logger.debug("** Vocabulary **")
        logger.debug(tv.vocabulary_)

        df_tmp = pl.DataFrame(
            data={
                "product_category": category,
                "term": tv.vocabulary_.keys(),
                "idx": tv.vocabulary_.values(),
            }
        )
        logger.debug(df_tmp.height)
        df_out.extend(df_tmp)
        logger.debug(df_out.height)

    df_out.write_csv(cfg.OUT_DIR + "/ords_vocabulary_problem.csv")

    df_out.group_by(["term"]).len(name="records").sort(
        "records", descending=True
    ).write_csv(cfg.OUT_DIR + "/ords_vocabulary_problem_freq.csv")


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    fit_products()
    fit_problem_text()
