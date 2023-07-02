#!/usr/bin/env python3

from funcs import *
import pandas as pd
from nltk import word_tokenize
from nltk import sent_tokenize
import nltk
logger = logfuncs.init_logger(__file__)
# Uncomment the following on first run.
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')

# Demonstration of common NLP methods taken from online tutorials.
# https://towardsdatascience.com/free-hands-on-tutorials-to-get-started-in-natural-language-processing-6a378e24dbfc
# https://towardsai.net/p/nlp/natural-language-processing-nlp-with-python-tutorial-for-beginners-1f54e610a1a0

# Read the data file as type string with na values set to empty string.
df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                 keep_default_na=False, na_values="")
# Filter for small subset with English language text.
df = df[df['country'].isin(['USA'])]
# Filter for decent length strings in the `problem` column.
df = df[(df['problem'].apply(lambda s: len(str(s)) > 24))]

categories = pd.read_csv(pathfuncs.ORDS_DIR +
                         '/{}.csv'.format(envfuncs.get_var('ORDS_CATS')))

for n in range(0, len(categories)):
    category = categories.iloc[n].product_category
    logger.debug('**** {} ****'.format(category))

    # Fetch a single string for demo purposes.
    data = df.loc[df.product_category == category]['problem']
    if not data.any():
        continue
    text = data.iloc[0]

    logger.debug('** TEXT **')
    logger.debug(text)

    logger.debug('** SENTENCES')
    sentences = sent_tokenize(text)
    logger.debug(sentences)

    logger.debug('** TOKENS **')
    tokens = word_tokenize(text)
    logger.debug(tokens)

    logger.debug('** NO PUNCTUATION **')
    words_no_punc = []
    for w in tokens:
        if w.isalpha():
            words_no_punc.append(w.lower())
    logger.debug(words_no_punc)

    logger.debug('** NO STOPWORDS **')
    from nltk.corpus import stopwords
    stopwords = stopwords.words("english")
    logger.debug(stopwords)
    clean_words = []
    for w in words_no_punc:
        if w not in stopwords:
            clean_words.append(w)
    logger.debug(clean_words)

    logger.debug('** COMMON TOKENS **')
    from nltk.probability import FreqDist
    fdist = FreqDist(clean_words)
    logger.debug(fdist.most_common(10))

    # Categorizing and Tagging Words
    # https://www.nltk.org/book/ch05.html

    for sentence in sentences:
        logger.debug('**** SENTENCE: "' + sentence + '"')

        logger.debug('**** TOKENS ****')
        tokenized_words = word_tokenize(sentence)
        tagged_words = nltk.pos_tag(tokenized_words)
        logger.debug(tagged_words)

        logger.debug('**** PARSED A ****')
        # Python nltk.RegexpParser() Examples
        # https://www.programcreek.com/python/example/91255/nltk.RegexpParser
        grammar = "NP : {<DT>?<JJ>*<NN>} "
        parser = nltk.RegexpParser(grammar)
        output = parser.parse(tagged_words)
        logger.debug(output)

        logger.debug('**** PARSED B ****')
        # Python nltk.RegexpParser() Examples
        # https://www.programcreek.com/python/example/91255/nltk.RegexpParser
        grammar = r""" NP : {<.*>+}
                        }<JJ>+{"""
        parser = nltk.RegexpParser(grammar)
        output = parser.parse(tagged_words)
        logger.debug(output)

        # Extracting Information from Text
        # https://www.nltk.org/book/ch07.html
        logger.debug('** NAMED ENTITIES ****')
        N_E_R = nltk.ne_chunk(tagged_words, binary=False)
        logger.debug(N_E_R)
