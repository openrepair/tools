#!/usr/bin/env python3

from langdetect import detect
from funcs import *
import pandas as pd
from langdetect import DetectorFactory
DetectorFactory.seed = 0

logger = logfuncs.init_logger(__file__)

# Detect languages in ORDS data using the Python langdetect package.

# https://github.com/Mimino666/langdetect
# This library is a direct port of Google's language-detection library from Java to Python. All the classes and methods are unchanged, so for more information see the project's website or wiki.
# Presentation of the language detection algorithm: http://www.slideshare.net/shuyo/language-detection-library-for-java.
# https://code.google.com/archive/p/language-detection/wikis/Tools.wiki


# Read the entire ORDS export.
data = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str)
logger.debug(data)
# Remove empty strings and group non-empty strings
data = pd.DataFrame(data=data['problem'].unique(), columns=[
                    'problem']).dropna().astype('str')

test=False
# For testing purposes you could filter for longer strings and shuffle the values.
if test:
    data = data[(data['problem'].apply(lambda s: len(str(s)) > 64))].sample(frac=0.1)

data['language'] = ''
data.reindex(copy=False)
logger.debug(data)
for i, row in data.iterrows():
    print(i)
    try:
        lang = detect(row.problem)
    except Exception as error:
        lang = ''
        print(row.problem)
        print(error)
        continue

    data.at[i, 'language'] = lang

data.to_csv(pathfuncs.OUT_DIR + '/ords_lang_detect.csv', index=False)
logger.debug(data)
