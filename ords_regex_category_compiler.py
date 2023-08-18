#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
logger = logfuncs.init_logger(__file__)


# Given a list of "terms" (actually mini-regexes), return a whole regular expression string for each category.
# The "terms" reside in dat/product_category_regex_elements.csv.
# They come from a Google sheet for ease of editing and testing. Free to copy for own use.
# https://docs.google.com/spreadsheets/d/1LVQrLXPupufRhh1aNR33R6ea3f57dcvz_QA3mumbJfQ/edit?usp=sharing


# Fetch regexes and test terms.
testterms = pd.read_csv(pathfuncs.DATA_DIR +
                        '/ords_testdata_common_products.csv')
rxelems = pd.read_csv(pathfuncs.DATA_DIR +
                      '/product_category_regex_elements.csv')
# Create a structure to hold compiled regexes.
results = pd.DataFrame(columns=['product_category', 'lang', 'regex'])
results['product_category'] = rxelems.columns
results['lang'] = 'any'
results['regex'] = ''

# Main loop.
for i, row in results.iterrows():
    category = row['product_category']
    print(category)
    logger.debug(category)
    data = rxelems[category]
    data.dropna(inplace=True)
    regex = miscfuncs.build_regex_string(data)
    rx = re.compile(regex)
    tests = testterms.loc[testterms.product_category == category]
    for n, test in tests.iterrows():
        logger.debug(test['product'])
        matches = rx.search(test['product'])
        logger.debug(matches)
    results.loc[i, 'regex'] = regex

# Write regex strings to csv format file.
results.to_csv(pathfuncs.OUT_DIR +
               '/product_category_regexes.csv', index=False)
