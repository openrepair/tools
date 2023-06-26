#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
logger = logfuncs.init_logger(__file__)


# Given a list of "terms" (actually mini-regexes), return a whole regular expression string for each category.
# The "terms" reside in dat/product_category_regex_elements.csv.
# They come from a Google sheet for ease of editing and testing. Free to copy for own use.
# https://docs.google.com/spreadsheets/d/1LVQrLXPupufRhh1aNR33R6ea3f57dcvz_QA3mumbJfQ/edit?usp=sharing


def compile_regex(terms, pre=True, aft=True):
    result = '(?i)('
    if (pre == True):
        result += '([a-zß-ÿœ]{3,}[ -]?)?'
    if (len(terms) > 0):
        result += '(' + '|'.join(list(set(terms))) + ')'
    if (aft == True):
        result += '([a-zß-ÿœ]{3,}[ -]?)?'
    result += ')'
    return result


# Fetch regexes and test terms.
testterms = pd.read_csv(pathfuncs.DATA_DIR +
                        '/ords_testdata_common_products.csv')
rxelems = pd.read_csv(pathfuncs.DATA_DIR +
                      '/product_category_regex_elements.csv')
# Create a structure to hold compiled regexes.
results = pd.DataFrame(columns=['product_category', 'lang', 'regex'])

# Main loop.
for category in rxelems.columns:
    print(category)
    logger.debug(category)
    results.loc[len(results)+1, 'product_category'] = category
    results.loc[len(results), 'lang'] = 'any'
    data = rxelems[category]
    data.dropna(inplace=True)
    regex = compile_regex(data)
    rx = re.compile(regex)
    tests = testterms.loc[testterms.product_category == category]
    for i in range(0, len(tests)):
        test = tests.iloc[i]
        logger.debug(test.values[1])
        matches = rx.search(test.values[1])
        logger.debug(matches)
    results.loc[len(results), 'regex'] = regex

# Write regex strings to csv format file.
results.to_csv(pathfuncs.OUT_DIR +
               '/product_category_regexes.csv', index=False)
