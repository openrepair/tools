#!/usr/bin/env python3

# Demonstration of common NLP methods taken from online tutorials.
# https://towardsdatascience.com/free-hands-on-tutorials-to-get-started-in-natural-language-processing-6a378e24dbfc
# https://towardsai.net/p/nlp/natural-language-processing-nlp-with-python-tutorial-for-beginners-1f54e610a1a0

import polars as pl
from nltk import word_tokenize
from nltk import sent_tokenize
import nltk
from funcs import *

if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("averaged_perceptron_tagger")
    nltk.download("maxent_ne_chunker")
    nltk.download("words")

    # Filter for small subset with English language text.
    # Filter for decent length strings in the `problem` column.
    df = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
    df_data = df.filter(
        pl.col("country") == pl.lit("USA"),
        pl.col("problem").str.len_chars() > 24,
    ).select(
        pl.col(
            "id",
            "product_category",
            "problem",
        )
    )

    df_cats = ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS"))

    for i, category in df_cats.iter_rows():
        logger.debug(f"**** {category} ****")

        # Fetch a single string for demo purposes.
        data = df_data.filter(
            pl.col("product_category") == pl.lit(category),
        ).select(
            pl.col(
                "problem",
            )
        )
        if len(data) == 0:
            continue

        text = data.item(0, 0)
        logger.debug("** TEXT **")
        logger.debug(text)

        logger.debug("** SENTENCES")
        sentences = sent_tokenize(text)
        logger.debug(sentences)

        logger.debug("** TOKENS **")
        tokens = word_tokenize(text)
        logger.debug(tokens)

        logger.debug("** NO PUNCTUATION **")
        words_no_punc = []
        for w in tokens:
            if w.isalpha():
                words_no_punc.append(w.lower())
        logger.debug(words_no_punc)

        logger.debug("** NO STOPWORDS **")
        from nltk.corpus import stopwords

        stopwords = stopwords.words("english")
        logger.debug(stopwords)
        clean_words = []
        for w in words_no_punc:
            if w not in stopwords:
                clean_words.append(w)
        logger.debug(clean_words)

        logger.debug("** COMMON TOKENS **")
        from nltk.probability import FreqDist

        fdist = FreqDist(clean_words)
        logger.debug(fdist.most_common(10))

        # Categorizing and Tagging Words
        # https://www.nltk.org/book/ch05.html

        for sentence in sentences:
            logger.debug('**** SENTENCE: "' + sentence + '"')

            logger.debug("**** TOKENS ****")
            tokenized_words = word_tokenize(sentence)
            tagged_words = nltk.pos_tag(tokenized_words)
            logger.debug(tagged_words)

            logger.debug("**** PARSED A ****")
            # Python nltk.RegexpParser() Examples
            # https://www.programcreek.com/python/example/91255/nltk.RegexpParser
            grammar = "NP : {<DT>?<JJ>*<NN>} "
            parser = nltk.RegexpParser(grammar)
            output = parser.parse(tagged_words)
            logger.debug(output)

            logger.debug("**** PARSED B ****")
            # Python nltk.RegexpParser() Examples
            # https://www.programcreek.com/python/example/91255/nltk.RegexpParser
            grammar = r""" NP : {<.*>+}
                            }<JJ>+{"""
            parser = nltk.RegexpParser(grammar)
            output = parser.parse(tagged_words)
            logger.debug(output)

            # Extracting Information from Text
            # https://www.nltk.org/book/ch07.html
            logger.debug("** NAMED ENTITIES ****")
            N_E_R = nltk.ne_chunk(tagged_words, binary=False)
            logger.debug(N_E_R)
