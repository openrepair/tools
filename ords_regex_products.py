#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re

logger = logfuncs.init_logger(__file__)


def build_regexes():

    rxelems = pd.read_csv(pathfuncs.DATA_DIR +
                          '/product_regex_elements.csv', dtype=str)
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
                   '/product_regexes.csv', index=True)
    return regexes


def precompile_regexes(regexes):
    regexes.dropna(inplace=True)
    for i, row in regexes.iterrows():
        regexes.at[i, 'rx'] = re.compile(row['regex'], flags=re.IGNORECASE+re.UNICODE)
    return regexes


def get_products(columns):

    df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                     keep_default_na=False, na_values="")
    df.rename(
        columns={'partner_product_category': 'product'}, inplace=True)
    df['product']= df['product'].apply(
        lambda s: s.split('~').pop().strip())
    df = df.reindex(columns=columns)
    df = df.groupby(columns).size().reset_index(name='records').sort_values(
        by=columns, key=lambda col: col.str.lower())
    df['matched'] = ''
    return df


def get_test_data(sample=0.25, columns=[], categories=[]):

    testterms = get_products(columns)
    if len(categories) > 0:
        testterms = testterms.loc[testterms['product_category'].isin(categories)]
    if sample < 1:
        testterms = testterms.sample(frac=sample)
    return testterms


def test_one(testterms, key, regexes):
    logger.debug('*** {} ***'.format(key))
    rx = regexes.at[key, 'rx']
    for n, term in testterms.iterrows():
        matches = rx.search(term['product'])
        matched = ''
        if matches != None:
            print("{}".format(term['product']))
            testterms.at[n, 'has-match'] = True
            matched = matches.group()
        testterms.at[n, 'matched'] = "{} : {}".format(key, matched)
    total = len(testterms)
    if total > 0:
        matched = len(testterms.loc[testterms['has-match'] == True])
        logger.debug('{} of {} matched = {}%'.format(
            matched, total, round(matched/total*100)))
    else:
        logger.debug('0 of 0 matched = 0%')
    return testterms


# Test terms from a set of categories agains a regex.
def test_pairs(regexes):
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
        ('computer-tablet', ['Tablet']),
        ('computer-desktop',  ['Desktop computer']),
        ('computer-laptop', ['Laptop']),
        ('computer-accessory', ['PC accessory']),
        ('computer-auto', ['Tablet', 'Handheld entertainment device',
                           'PC accessory', 'TV and gaming-related accessories']),
        ('printer', ['Printer/scanner']),
        ('telecom', ['Small home electrical', 'Misc']),
        ('telecom-mobile', ['Mobile']),
        ('headphone', ['Headphones']),
        ('set-top-box', ['TV and gaming-related accessories']),
        ('camera', ['Digital compact camera', 'DSLR/video camera']),
        ('flatpanel-screen', ['Flat screen']),
        ('lighting', ['Lamp', 'Decorative or safety lights']),
        ('power-tool', ['Power tool']),
        ('garden-machine', ['Power tool', 'Large home electrical']),
        ('shredder', ['Paper shredder']),
        ('projector', ['Projector']),
        ('toaster', ['Toaster']),
        ('watch-clock', ['Watch/clock']),
        ('hairdryer', ['Hair dryer']),
        ('food-processor', ['Food processor']),
        ('charger-adapter', ['Battery/charger/adapter']),
        ('musical-instrument', ['Musical instrument']),
        ('small-kitchen', ['Small kitchen item']),
        ('small-domestic', ['Small home electrical']),
        ('personal-medical', ['Hair & beauty item',
         'Small home electrical', 'Misc']),
        ('personal-grooming', ['Hair & beauty item']),
        ('personal-hygiene', ['Hair & beauty item']),
        ('heater', ['Small home electrical', 'Misc']),
        ('toy', ['Toy']),
    ]
    dftest = pd.DataFrame()
    for i in range(0, len(pairs)):
        data = get_test_data(sample=1, columns=[
                             'product_category', 'product'], categories=pairs[i][1])
        data['has-match'] = False
        test = test_one(data, pairs[i][0], regexes)
        dftest = pd.concat([dftest, test])

    testmatches = dftest.loc[dftest['has-match'] == True].sort_values(
        by=['product_category', 'matched'], ascending=[True, True])
    testmatches.to_csv(pathfuncs.OUT_DIR +
                       '/products_regex_pairs_matched.csv', index=False)
    testmisses = dftest.loc[dftest['has-match'] == False].sort_values(
        by=['product_category', 'matched'], ascending=[True, True])
    testmisses.to_csv(pathfuncs.OUT_DIR +
                      '/products_regex_pairs_missed.csv', index=False)


# Test each term against each regex.
def test_all(regexes):
    testterms = get_test_data(sample=1, columns=['product'])
    for n, term in testterms.iterrows():
        print("{}".format(term['product']))
        matched = []
        for key, regex in regexes.iterrows():
            matches = regex.rx.search(term['product'])
            if matches != None:
                matched.append("({}:{})".format(key, matches.group()))
        testterms.at[n, 'matched'] = "|".join(matched)

    testmatches = testterms.loc[testterms['matched'] > ''].sort_values(
        by=['product', 'matched'], ascending=[True, True])
    testmatches.to_csv(pathfuncs.OUT_DIR +
                       '/products_regex_all_matched.csv', index=False)
    testmisses = testterms.loc[testterms['matched'] == ''].sort_values(
        by=['product', 'matched'], ascending=[True, True])
    testmisses.to_csv(pathfuncs.OUT_DIR +
                      '/products_regex_all_missed.csv', index=False)


regexes = precompile_regexes(build_regexes())
test_pairs(regexes)
test_all(regexes)
