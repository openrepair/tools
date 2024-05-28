#!/usr/bin/env python3

import polars as pl
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk

nltk.download("punkt")
nltk.download("wordnet")
nltk.download("stopwords")
from funcs import *


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        self.rx = re.compile("[\W\d_]")

    def __call__(self, doc):
        return [
            self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))
        ]


def log_vectors(title):

    logger.debug("**** {} ****".format(title))

    logger.debug("** STOP WORDS **")
    logger.debug(vectorizer.get_stop_words())

    logger.debug("** VOCABULARY **")
    logger.debug(vectorizer.vocabulary_)

    logger.debug("** FEATURE NAMES **")
    logger.debug(vectorizer.get_feature_names_out())

    # Calculate similarity
    # cosine_similarities = linear_kernel(
    #     docvects[0:1], docvects).flatten()
    # docscores = [item.item() for item in cosine_similarities[1:]]
    # logger.debug('** SIMILARITY **')
    # logger.debug(docscores)

    # logger.debug('** BAG OF WORDS **')
    # logger.debug(doc_vectors.toarray())


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    docs = list(
        pl.read_csv(cfg.DATA_DIR + "/quests/vacuums/dustup.csv")
        .filter(pl.col("country") == pl.lit("USA"))
        .select(
            pl.col("id_ords"),
            pl.col("fault_type"),
            pl.col("problem"),
        )["problem"]
    )

    vectorizer = TfidfVectorizer()
    docvects = vectorizer.fit_transform(docs)
    log_vectors("#1 DEFAULT")

    stop_words = set(stopwords.words("english"))
    tokenizer = LemmaTokenizer()
    token_stop = tokenizer(" ".join(stop_words))
    vectorizer = TfidfVectorizer(stop_words=token_stop, tokenizer=tokenizer)
    docvects = vectorizer.fit_transform(docs)
    log_vectors("#2 WITH STOPWORDS")
