#!/usr/bin/env python3

from funcs import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
# Uncomment if not already downloaded.
# nltk.download('punkt')

logger = logfuncs.init_logger(__file__)


# Using quest data for a single product category.
def get_docs():

    df = pd.read_csv(pathfuncs.DATA_DIR + '/quests/vacuums/dustup.csv',
                     dtype=str, keep_default_na=False, na_values="")
    # Filter for small subset with English language text.
    data = df[df['country'].isin(['USA'])]
    # Select useful columns.
    data = data.reindex(columns=['id_ords', 'fault_type', 'problem'])
    return data['problem'].reset_index(drop=True).squeeze().dropna().unique()


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        self.ignore_tokens = [',', '.', ';', ':', '"', '``',
                              "''", '`', '&', '!', '~', '#', '?', '+', '(', ')']

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]


def log_vectors(title):

    logger.debug('**** {} ****'.format(title))

    logger.debug('** STOP WORDS **')
    logger.debug(vectorizer.get_stop_words())

    logger.debug('** VOCABULARY **')
    logger.debug(vectorizer.vocabulary_)

    logger.debug('** FEATURE NAMES **')
    logger.debug(vectorizer.get_feature_names_out())

    # Calculate similarity
    # cosine_similarities = linear_kernel(
    #     docvects[0:1], docvects).flatten()
    # docscores = [item.item() for item in cosine_similarities[1:]]
    # logger.debug('** SIMILARITY **')
    # logger.debug(docscores)

    # logger.debug('** BAG OF WORDS **')
    # logger.debug(doc_vectors.toarray())


docs = get_docs()

vectorizer = TfidfVectorizer()
docvects = vectorizer.fit_transform(docs)
log_vectors('#1 DEFAULT')

stop_words = set(stopwords.words('english'))
tokenizer = LemmaTokenizer()
token_stop = tokenizer(' '.join(stop_words))
vectorizer = TfidfVectorizer(stop_words=token_stop, tokenizer=tokenizer)
docvects = vectorizer.fit_transform(docs)
log_vectors('#2 WITH STOPWORDS')
