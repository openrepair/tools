#!/usr/bin/env python3

from funcs import *
import pandas as pd
import json

logger = logfuncs.init_logger(__file__)


def write_json(text, suffix):

    path = pathfuncs.OUT_DIR + '/wikidata_{}.json'.format(suffix)
    content = json.loads(text)
    with open(path, 'w') as f:
        json.dump(content, f, indent=4, ensure_ascii=False)
    return content


def write_text(text, suffix):

    path = pathfuncs.OUT_DIR + '/wikidata_{}.txt'.format(suffix)
    with open(path, 'w') as f:
        f.write(text)
    return text


def read_file_item(key):
    data = {}
    path = pathfuncs.OUT_DIR + '/wikidata_{}.json'.format(key)
    if not pathfuncs.check_path(path):
        print('File not found! {}'.format(path))
        return False
    with open(path) as schema_file:
        content = schema_file.read()

    parsed = json.loads(content)

    data = {
        'key': key,
        'label_langs': 0,
        'desc_langs': 0,
        'alias_langs': 0,
        'statements': 0,
        'sitelinks': 0,
        'label_en': 'No English label',
        'desc_en': 'No English description',
        'alias_en': 'No English aliases',
    }

    if 'labels' in parsed:
        data['label_langs'] = len(parsed['labels'])
        if 'en' in parsed['labels']:
            data['label_en'] = parsed['labels']['en']

    if 'descriptions' in parsed:
        data['desc_langs'] = len(parsed['descriptions'])
        if 'en' in parsed['descriptions']:
            data['desc_en'] = parsed['descriptions']['en']

    if 'aliases' in parsed:
        data['alias_langs'] = len(parsed['aliases'])
        if 'en' in parsed['aliases']:
            data['alias_en'] = parsed['aliases']['en']

    if 'statements' in parsed:
        data['statements'] = len(parsed['statements'])

    if 'sitelinks' in parsed:
        data['sitelinks'] = len(parsed['sitelinks'])

    return data


def read_file_subclasses(key):
    keys = []
    suffix = "{}_subclasses".format(key)
    path = pathfuncs.OUT_DIR + '/wikidata_{}.json'.format(suffix)
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


def fetch_keys_fields(keys):
    api = wkdfuncs.wikidataRestApi()
    for key in keys:
        res = api.fetch_fields(key)
        logger.debug(key)
        if res.status_code == 200:
            json = write_json(res.text, key)
            label = 'No English label'
            if 'labels' in json:
                if 'en' in json['labels']:
                    label = json['labels']['en']
            logger.debug(label)
        else:
            logger.debug(res.status_code)


def fetch_keys_statements(keys):
    api = wkdfuncs.wikidataRestApi()
    skey = 'P279'
    for key in keys:
        res = api.fetch_statement(key, skey)
        suffix = "{}_{}".format(key, skey)
        if res.status_code == 200:
            write_json(res.text, suffix)
            logger.debug(suffix)
        else:
            logger.debug(res.status_code)


def fetch_subclasses(key):
    api = wkdfuncs.wikidataSparqlAPI()
    res = api.fetch_subclasses(key)
    suffix = "{}_subclasses".format(key)
    if res.status_code == 200:
        write_json(res.text, suffix)
        logger.debug(suffix)
    else:
        logger.debug(res.status_code)


def fetch_to_file(keys):
    fetch_keys_fields(keys)
    fetch_keys_statements(keys)
    for key in keys:
        fetch_subclasses(key)


def fetch_from_file_subclasses(keys):
    for key in keys:
        keys = read_file_subclasses(key)
        logger.debug(keys)
        fetch_keys_fields(keys)


def parse_items(keys):
    for key, desc in keys.items():
        subs = read_file_subclasses(key)
        d = []
        for subkey in subs:
            data = read_file_item(subkey)
            logger.debug(data)
            print(data['label_en'])
            d.append(data)

        df = pd.DataFrame(data=d, columns=data.keys())
        df.sort_values(by='label_en', inplace=True)
        df.to_csv(pathfuncs.OUT_DIR + '/wikidata_{}_{}.csv'.format(key,
                  desc.replace(' ', '-')), index=False)


# START

# QUICK API TESTS
# api = wkdfuncs.wikidataRestApi()
# test = api.get_headers()
# spq = wkdfuncs.wikidataSparqlAPI()
# test = spq.get_headers()
# keys = ['Q62927'] # digital camera (Q62927)
# fetch_keys_fields(keys)

# These returned no subclasses!
# keys = {
    # 'Q8946856' : 'Category:Electrical apparatus',
    # 'Q9016839' : 'Category:Electrical equipment',
    # 'Q9412449' : 'Category:Electrical appliances',
    # 'Q8411527' : 'Category:Electronic toys',
# }

# keys = {
#     'Q2858615': 'electronic machine',
#     'Q581105':  'consumer electronics',
#     'Q3749263': 'electrical device',
#     'Q2425052': 'electrical appliance',
#     'Q116961643': 'electronic product',
#     'Q65280844': 'electronic system',
#     'Q107618851': 'Electrical device',
#     'Q3749263': 'electrical device',
#     'Q14859880': 'audio electronics',
#     'Q212920': 'home appliance',
#     'Q3966': 'computer hardware',
#     'Q1327701' : 'power tool',
#     'Q117710711' : 'electric power tool',
#     'Q115922057' : 'health care or beauty item',
#     'Q10528974' : 'personal hygiene item',
#     'Q2249149' : 'electronic game',
#     'Q15654425' : 'electronic toy',
#     'Q5639584' : 'hairstyling tool',
#     'Q12269769' : 'major appliance',
#     'Q20076681' : 'electric household appliance',
# }

# electronic waste (Q327400)
keys = {}
fetch_to_file(keys.keys())
fetch_from_file_subclasses(keys.keys())
parse_items(keys)
