#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re

logger = logfuncs.init_logger(__file__)


# Given a list of "terms" (actually mini-regexes), return a whole regular expression string for each key.


def build_regexes():

    rxelems = pd.read_csv(pathfuncs.DATA_DIR +
                          '/device_regex_elements.csv', dtype=str)
    regexes = pd.DataFrame(columns=['key', 'regex'])
    logger.debug(rxelems.columns)
    regexes['key'] = rxelems.columns.values
    regexes['regex'] = ''
    regexes.set_index('key', inplace=True)
    for key, row in regexes.iterrows():
        print("{}".format(key))
        terms = rxelems[key].dropna()
        if (len(terms) > 0):
            regexes.loc[key, 'regex'] = miscfuncs.build_regex_string(terms)
    regexes.to_csv(pathfuncs.OUT_DIR +
                   '/devices_regexes.csv', index=True)
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

    testterms = slice_item_types()
    testterms['matched'] = ''
    testterms['keys'] = ''
    if len(categories) > 0:
        testterms = testterms.loc[testterms.product_category.isin(categories)]
    if sample < 1:
        testterms = testterms.sample(frac=sample)
    return testterms


# test each test term for a single item_type.
def test_one(testterms, key, regexes):
    logger.debug('*** {} ***'.format(key))
    rx = regexes.at[key, 'rx']
    for n, term in testterms.iterrows():
        matches = rx.search(term['item_type'])
        if matches != None:
            print("{}".format(term['item_type']))
            testterms.at[n, 'matched'] = matches.group()
            testterms.at[n, 'keys'] = key
    testterms.sort_values(by=['keys', 'product_category', 'matched'], ascending=[
                          False, True, True], inplace=True)
    testterms.to_csv(pathfuncs.OUT_DIR +
                     '/devices_regex_matches_{}.csv'.format(key), index=False)
    total = len(testterms)
    if total > 0:
        matched = len(testterms.loc[testterms['keys'] != ''])
        logger.debug('{} of {} matched = {}%'.format(
            matched, total, round(matched/total*100)))
    else:
        logger.debug('0 of 0 matched = 0%')


regexes = precompile_regexes(build_regexes())

pairs = [
    ('iron', ['Iron']),
    ('coffee-machine', ['Coffee maker']),
    ('kettle', ['Kettle']),
    ('microwave', ['Large home electrical']),
    ('lawnmower', ['Large home electrical']),
    ('sport-exercise', ['Large home electrical']),
    ('garden-machine', ['Large home electrical']),
    ('sewing-machine', ['Sewing machine']),
    ('portable-audio-video', ['Handheld entertainment device']),
    ('small-tablet', ['Tablet', 'Handheld entertainment device',
     'PC accessory', 'TV and gaming-related accessories']),
    ('gaming-console', ['Handheld entertainment device']),
    ('gaming-portable', ['Handheld entertainment device']),
    ('speaker', ['Handheld entertainment device', 'TV and gaming-related accessories',
     'PC accessory', 'Hi-Fi separates', 'Hi-Fi integrated']),
    ('remote-control', ['Handheld entertainment device',
     'PC accessory', 'TV and gaming-related accessories']),
    ('dishwasher', ['Large home electrical']),
    ('washing-machine', ['Large home electrical']),
    ('clothes-dryer', ['Large home electrical']),
    ('fridge', ['Large home electrical']),
    ('freezer', ['Large home electrical']),
    ('air-conditioner', ['Aircon/dehumidifier']),
    ('vacuum-cleaner', ['Vacuum']),
    ('tablet', ['Tablet']),
    ('desktop',  ['Desktop computer']),
    ('laptop', ['Laptop']),
    ('printer', ['Printer/scanner']),
    ('telecom', ['Small home electrical', 'Misc']),
    ('mobile', ['Mobile']),
    ('headphone', ['Headphones']),
    ('set-top-box', ['TV and gaming-related accessories']),
    ('camera', ['Digital compact camera', 'DSLR/video camera']),
    ('flatpanel-screen', ['Flat screen']),
    ('lighting', ['Lamp', 'Decorative or safety lights']),
    ('power-tool', ['Power tool']),
    ('garden-machine', ['Power tool', 'Large home electrical']),
    ('shredder', ['Paper shredder']),
    ('personal-electronic', ['Hair & beauty item',
    'Small home electrical', 'Misc']),
    ('projector', ['Projector']),
    ('toaster', ['Toaster']),
    ('watch-clock', ['Watch/clock']),
    ('hairdryer', ['Hair dryer']),
    ('food-processor', ['Food processor']),
    ('charger-adapter', ['Battery/charger/adapter']),
]
for i in range(0, len(pairs)):
    data = get_test_data(sample=1, categories=pairs[i][1])
    test_one(data, pairs[i][0], regexes)
