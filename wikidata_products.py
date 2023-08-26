#!/usr/bin/env python3

from funcs import *
import pandas as pd
import numpy as np
import json

logger = logfuncs.init_logger(__file__)

# For each language get each label and alias.


def read_file_item(key):

    baselang = 'en'
    langs = ['de', 'nl', 'fr', 'es', 'it', 'da']
    path = pathfuncs.DATA_DIR + '/tmp/wikidata/wikidata_{}.json'.format(key)
    if not pathfuncs.check_path(path):
        print('File not found! {}'.format(path))
        return False
    with open(path) as schema_file:
        content = schema_file.read()

    parsed = json.loads(content)

    data = []
    if 'labels' in parsed:
        if baselang in parsed['labels']:
            label = parsed['labels'][baselang]
            data.append([key, label, baselang, label])
            for lang in langs:
                if lang in parsed['labels']:
                    if baselang in parsed['aliases']:
                        for alias in parsed['aliases'][baselang]:
                            data.append([key, label, baselang, alias])

                    if lang in parsed['aliases']:
                        for alias in parsed['aliases'][lang]:
                            data.append([key, label, lang, alias])

    return data


# NOTE json was generated once and copied to a tmp dir
# to avoid constant calls to Wikidata API.
# See wikidata_product_categories.py
def read_file_subclasses(key):
    keys = []
    suffix = "{}_subclasses".format(key)
    path = pathfuncs.DATA_DIR + '/tmp/wikidata/wikidata_{}.json'.format(suffix)
    if not pathfuncs.check_path(path):
        print('File not found! {}'.format(path))
        return False
    with open(path) as schema_file:
        content = schema_file.read()

    parsed = json.loads(content)
    bindings = parsed['results']['bindings']
    for elem in bindings:
        key = elem['item']['value'].replace(
            'http://www.wikidata.org/entity/', '')
        keys.append(key)
    return keys


def get_item_types(keys):

    cols = ['wikidata', 'label', 'language', 'alias']
    df = pd.DataFrame(columns=cols)
    for key, desc in keys.items():
        subs = read_file_subclasses(key)
        for subkey in subs:
            data = read_file_item(subkey)
            if len(data) > 0:
                df = pd.concat(
                    [df, pd.DataFrame(data=np.array(data), columns=cols)])

    df.drop_duplicates(subset=['label', 'language', 'alias'], inplace=True)
    df.sort_values(by=['label', 'language', 'alias'], inplace=True)
    logger.debug(df)
    df.to_csv(pathfuncs.OUT_DIR + '/wikidata_product_langs.csv', index=False)


keys = {
    'Q2858615': 'electronic machine',
    'Q581105':  'consumer electronics',
    'Q3749263': 'electrical device',
    'Q2425052': 'electrical appliance',
    'Q116961643': 'electronic product',
    'Q65280844': 'electronic system',
    'Q107618851': 'Electrical device',
    'Q3749263': 'electrical device',
    'Q14859880': 'audio electronics',
    'Q212920': 'home appliance',
    'Q3966': 'computer hardware',
    'Q1327701': 'power tool',
    'Q117710711': 'electric power tool',
    'Q115922057': 'health care or beauty item',
    'Q10528974': 'personal hygiene item',
    'Q2249149': 'electronic game',
    'Q15654425': 'electronic toy',
    'Q5639584': 'hairstyling tool',
    'Q12269769': 'major appliance',
    'Q20076681': 'electric household appliance',
}

get_item_types(keys)
