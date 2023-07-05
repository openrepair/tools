#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
import requests
from html.parser import HTMLParser
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize

logger = logfuncs.init_logger(__file__)

# Extract a vocabulary from a restarters.net wiki page for an ORDS category (Vacuum).


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
        # Remove numbers and punctuation.
        self.rx = re.compile('[\W\d_]')

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if (not self.rx.search(t))]


# [Simple HTML and XHTML parser](https://docs.python.org/3/library/html.parser.html)
class WikiHTMLParser(HTMLParser):
    lines = []

    def handle_data(self, data):
        if self.lasttag == 'p':
            print(data)
            line = data.strip()
            if line > '':
                self.lines.append(line)


def fetch_text(url):
    r = requests.get(url)
    parser = WikiHTMLParser()
    if r.status_code == 200:
        parser.feed(r.text)
    return parser.lines


tokenizer = LemmaTokenizer()

# [Using stop words](https://scikit-learn.org/stable/modules/feature_extraction.html#stop-words)
# [Stop Word Lists in Free Open-source Software Packages](https://aclanthology.org/W18-2502/)
# [Stopword Lists for 19 Languages](https://www.kaggle.com/datasets/rtatman/stopword-lists-for-19-languages)
stopfile1 = open(pathfuncs.DATA_DIR + '/stopwords-english.txt', "r")
# ORDS corpus custom stopwords.
stopfile2 = open(pathfuncs.DATA_DIR + '/stopwords-english-repair.txt', "r")
stoplist = stopfile1.read().replace("\n", ' ') + \
    stopfile2.read().replace("\n", ' ')
stopfile1.close()
stopfile2.close()
# Use same tokenizer on stopwords as used in the vectorizer.
stop_tokens = tokenizer(stoplist)

tv = TfidfVectorizer(stop_words=stop_tokens, tokenizer=tokenizer)

logger.debug('*** STOPWORDS ***')
logger.debug(tv.get_stop_words())

sentences = fetch_text('https://wiki.restarters.net/Vacuum_cleaners')
logger.debug(sentences)

tv.fit_transform(sentences)

logger.debug('** VOCABULARY **')
logger.debug(tv.vocabulary_)

df = pd.DataFrame({'term': tv.vocabulary_.keys(),
                  'idx': tv.vocabulary_.values()})
df.sort_values(by=['idx', 'term'],
               ascending=True, inplace=True, ignore_index=True)

path = pathfuncs.OUT_DIR + '/ords_vocabulary_wiki_Vacuum.csv'
df.to_csv(path, index=False)
