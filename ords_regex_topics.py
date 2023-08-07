#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re

logger = logfuncs.init_logger(__file__)

# Multi-lingual regex search for random themes within the ORDS `partner_product_category` values.


# Split the partner_product_category string.
def get_item_types(df):
    dfp = df['partner_product_category'].reset_index(drop=True).squeeze()
    np_res = dfp.str.split('~').str.get(1).str.strip().dropna().unique()
    return np_res


df = pd.read_csv(pathfuncs.path_to_ords_csv())
df.dropna(subset="partner_product_category", inplace=True, ignore_index=True)

topics = pd.DataFrame(data={
    'topic': ['Christmas', 'Bake-Off', 'Entertainment'],
    'rxcmp': [None,None,None],
    'rxstr': [
        miscfuncs.build_regex_string([
            "[yj]ule?", "(christ|x)mas", "fairy", "fatate", "fe lys", "féériques", "hadas?", "kerst",
            "lichterketten", "[^ku]n[ei]v[ei]", "natale", "navidad", "neige", "no[ëe]l", "reindeer", "rendier",
            "rensdyr", "rentier", "santa", "schlitten", "schnee", "slæde", "sleigh",
            "slitta", "sneeew", "snow", "sprookjes", "traîneau", "trineo", "weihnacht"
        ]),
        miscfuncs.build_regex_string([
            '[wv]a[f]+[el]{2}', 'bisc(ui|o)t(t[io])?', 'biscuit', 'bollo', 'br(ea|oo)d', 'br[øo]{1,2}[dt]', 'cake',
            'cialda', 'cr[êe]pe', 'g(au|o)[f]+re', 'galleta', 'gâteau', 'k[ie]ks', 'kage', 'krepp', 'kuchen',
            'pains?$', 'pan(cake|nenkoek|dekage|ini)', 'pastel', 'pfannkuchen', 'scone', 't[a]+rt', 'tort([ea]|ita)'
        ]),
        miscfuncs.build_regex_string([
            '[ck]assette','dis[ck][ -]?man','game[ -]?boy','i[ -]?pod','mp[ -]?3','walk[ -]?man','atari','sega',
            'nintendo','x[ -]?box','transistor','dab','vhs','vcr','pvr','video','ps[ -]?[1-9]'
        ])
    ]})


for i, row in topics.iterrows():
    logger.debug(row.topic)
    logger.debug(row.rxstr)
    topics.at[i, 'rxcmp'] = re.compile(row.rxstr)

itemtypes = get_item_types(df)
for i, row in topics.iterrows():
    matched = []
    logger.debug('*** {} ***'.format(row.topic))
    for item in itemtypes:
        matches = row.rxcmp.search(item)
        if matches != None:
            logger.debug(matches.group())
            matched.append(item)

    pattern = "|".join(matched)
    logger.debug(pattern)
    results = df.loc[df.partner_product_category.str.contains(pattern)]
    results.to_csv(pathfuncs.OUT_DIR +
                   '/ords_regex_topic_{}.csv'.format(row.topic), index=False)
