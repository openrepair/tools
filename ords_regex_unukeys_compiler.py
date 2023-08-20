#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
logger = logfuncs.init_logger(__file__)


# Given a list of "terms" (actually mini-regexes), return a whole regular expression string for each category.
# The "terms" reside in dat/product_category_regex_elements.csv.
# They come from a Google sheet for ease of editing and testing. Free to copy for own use.
# https://docs.google.com/spreadsheets/d/1LVQrLXPupufRhh1aNR33R6ea3f57dcvz_QA3mumbJfQ/edit?usp=sharing


def build_regexes():

    unukeys = pd.read_csv(pathfuncs.DATA_DIR +
                          '/unu_keys.csv', dtype=str)
    regexes = pd.DataFrame(columns=['key', 'lang', 'regex'])
    rxelems = pd.read_csv(pathfuncs.DATA_DIR +
                          '/unukey_regex_elements.csv', dtype=str)
    regexes['key'] = rxelems.columns.values
    regexes['lang'] = 'any'
    regexes['regex'] = ''
    regexes = regexes.set_index(
        'key').join(unukeys.set_index('key'))
    print(regexes.index)
    for key, row in regexes.iterrows():
        print("{} ~ {}".format(key, row['description']))
        data = rxelems[key].dropna()
        if (len(data) > 0):
            regexes.loc[key, 'regex'] = miscfuncs.build_regex_string(data)
    regexes.drop(columns=['description', 'parent'], inplace=True)
    regexes.to_csv(pathfuncs.OUT_DIR +
                   '/unukey_regexes.csv', index=True)
    return regexes


def precompile_regexes(regexes):
    regexes.dropna(inplace=True)
    for i, row in regexes.iterrows():
        regexes.at[i, 'rx'] = re.compile(row['regex'], re.I)
    return regexes


def slice_item_types():

    df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                     keep_default_na=False, na_values="")
    df = df.reindex(
        columns=['product_category', 'partner_product_category'])
    df.rename(
        columns={'partner_product_category': 'item_type'}, inplace=True)
    df.item_type = df.item_type.apply(
        lambda s: s.split('~').pop().strip())
    df = df.groupby(['product_category', 'item_type']).size().reset_index(
        name='records').sort_values(['product_category', 'records'], ascending=[True, False])
    return df


def get_test_data(sample=0.25, categories=[]):

    unumap = pd.read_csv(pathfuncs.DATA_DIR +
                         '/ords_product_category_unu_key_map.csv', dtype=str)
    unumap.drop(columns=['unu_1995', 'unu_2000', 'unu_2005',
                         'unu_2010', 'unu_2011', 'unu_2012'], inplace=True)
    unumap.rename(columns={'unu_key': 'map_key',
                           'unu_desc': 'map_desc'}, inplace=True)

    # testterms = pd.read_csv(pathfuncs.DATA_DIR +
    #                         '/ords_testdata_common_products.csv')
    # testterms.rename(columns={'product': 'item_type'}, inplace=True)
    testterms = slice_item_types()
    testterms['matched'] = ''
    testterms['keys'] = ''

    if len(categories) > 0:
        testterms = testterms.loc[testterms.product_category.isin(categories)]
    if sample < 1:
        testterms = testterms.sample(frac=sample)

    logger.debug("{} test terms".format(len(testterms)))
    testterms = pd.merge(testterms.reset_index(), unumap,  how='inner',
                         left_on=['product_category'],
                         right_on=['product_category']).set_index('index')
    return testterms


# test each term against each regex.
def test_all(testterms, regexes):
    for n, term in testterms.iterrows():
        matched = []
        keys = []
        for key, row in regexes.iterrows():
            print("{} => {}".format(term['item_type'], key))
            matches = row['rx'].search(term['item_type'])
            if matches != None:
                matched.append(matches.group())
                keys.append(key)

        matched = '|'.join(list(set(matched)))
        keys = '|'.join(list(set(keys)))
        testterms.at[n, 'matched'] = matched
        testterms.at[n, 'keys'] = keys

    testterms['correct'] = testterms['map_key'] == testterms['keys']
    testterms.to_csv(pathfuncs.OUT_DIR +
                     '/unukey_regex_matches_all.csv', index=False)
    log_stats(testterms, 'test_all')


# test each term against all regexes except own mapped regex.
def test_other(testterms, regexes):
    for n, term in testterms.iterrows():
        matched = []
        keys = []
        for key, row in regexes.iterrows():
            if key != term['map_key']:
                print("{} => {}".format(term['item_type'], key))
                matches = row['rx'].search(term['item_type'])
                if matches != None:
                    matched.append(matches.group())
                    keys.append(key)

        matched = '|'.join(list(set(matched)))
        keys = '|'.join(list(set(keys)))
        testterms.at[n, 'matched'] = matched
        testterms.at[n, 'keys'] = keys

    testterms['correct'] = testterms['map_key'] == testterms['keys']
    testterms.to_csv(pathfuncs.OUT_DIR +
                     '/unukey_regex_matches_other.csv', index=False)
    log_stats(testterms, 'test_other')


# test each term with the regex for its own mapped unu key.
def test_mapkey(testterms, regexes):
    for n, term in testterms.iterrows():
        rx = regexes.loc[term['map_key']]['rx']
        print("{} => {}".format(term['item_type'], term['map_key']))
        matches = rx.search(term['item_type'])
        if matches != None:
            testterms.at[n, 'matched'] = matches.group()
            testterms.at[n, 'keys'] = term['map_key']

    testterms['correct'] = testterms['map_key'] == testterms['keys']
    testterms.to_csv(pathfuncs.OUT_DIR +
                     '/unukey_regex_matches_mapkey.csv', index=False)
    log_stats(testterms, 'test_mapkey')


# test each term with the regex for its own mapped unu key.
def test_one2one(testterms, regex):
    for n, term in testterms.iterrows():
        rx = regex['rx']
        print("{} => {}".format(term['item_type'], term['map_key']))
        matches = rx.search(term['item_type'])
        if matches != None:
            testterms.at[n, 'matched'] = matches.group()
            testterms.at[n, 'keys'] = term['map_key']
    testterms['correct'] = testterms['map_key'] == testterms['keys']
    testterms.to_csv(pathfuncs.OUT_DIR +
                     '/unukey_regex_matches_one2one.csv', index=False)
    log_stats(testterms, 'test_one2one')


def log_stats(df, type):
    import numpy as np
    logger.debug('*** STATS {} ***'.format(type))
    dfg = np.round(pd.pivot_table(df, values='records',
                                  index=['product_category'],
                                  columns=['correct'],
                                  aggfunc=['count'],
                                  fill_value=0,
                                  margins=True,
                                  margins_name='total'), 2)
    dfg.reset_index()
    dfg = pd.DataFrame(data=dfg.values, columns=[
                       'false', 'true', 'total'], index=dfg.index)
    logger.debug(dfg)
    dfg.to_csv(pathfuncs.OUT_DIR +
               '/unukey_regex_matches_stats_{}.csv'.format(type), index=True)


"""
Extract good matches for validation
Identify missing matches
Identify mismatches
"""

umbrellas = [
    "Hair & beauty item",
    "Handheld entertainment device",
    "Large home electrical",
    "Power tool",
    "Small home electrical"
]
misc = [
    "Misc"
]

# data = get_test_data(sample=0.1, categories=['Headphones'])
data = get_test_data(sample=1, categories=[])
# data = get_test_data(sample=0.5, categories=umbrellas)
# data = get_test_data(sample=1, categories=misc)
regexes = precompile_regexes(build_regexes())
# test_one2one(data, regexes.loc['401'])
test_mapkey(data, regexes)
# test_other(data, regexes)
# test_all(data, regexes)
