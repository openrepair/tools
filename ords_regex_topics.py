#!/usr/bin/env python3

# Multi-lingual regex search for random themes within the ORDS `partner_product_category` values.

import polars as pl
import re
from funcs import *


# Split the partner_product_category string.
def get_item_types(df):
    data = (
        df.select(pl.col("partner_product_category"))
        .with_columns(
            pl.col("partner_product_category")
            .str.split("~")
            .list.last()
            .str.strip_chars()
            .alias("item_type")
        )
        .drop_nulls()
        .unique()
    )
    return data


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    topics = pl.DataFrame(
        data={
            "topic": ["Christmas", "Bake-Off", "Entertainment"],
            "rx": [None, None, None],
            "patt": [
                textfuncs.build_regex_string(
                    [
                        "[yj]ule?",
                        "(christ|x)mas",
                        "fairy",
                        "fatate",
                        "fe lys",
                        "féériques",
                        "hadas?",
                        "kerst",
                        "lichterketten",
                        "[^ku]n[ei]v[ei]",
                        "natale",
                        "navidad",
                        "neige",
                        "no[ëe]l",
                        "reindeer",
                        "rendier",
                        "rensdyr",
                        "rentier",
                        "santa",
                        "schlitten",
                        "schnee",
                        "slæde",
                        "sleigh",
                        "slitta",
                        "sneeew",
                        "snow",
                        "sprookjes",
                        "traîneau",
                        "trineo",
                        "weihnacht",
                    ]
                ),
                textfuncs.build_regex_string(
                    [
                        "[wv]a[f]+[el]{2}",
                        "bisc(ui|o)t(t[io])?",
                        "biscuit",
                        "bollo",
                        "br(ea|oo)d",
                        "br[øo]{1,2}[dt]",
                        "cake",
                        "cialda",
                        "cr[êe]pe",
                        "g(au|o)[f]+re",
                        "galleta",
                        "gâteau",
                        "k[ie]ks",
                        "kage",
                        "krepp",
                        "kuchen",
                        "pains?$",
                        "pan(cake|nenkoek|dekage|ini)",
                        "pastel",
                        "pfannkuchen",
                        "scone",
                        "t[a]+rt",
                        "tort([ea]|ita)",
                    ]
                ),
                textfuncs.build_regex_string(
                    [
                        "[ck]assette",
                        "dis[ck][ -]?man",
                        "game[ -]?boy",
                        "i[ -]?pod",
                        "mp[ -]?3",
                        "walk[ -]?man",
                        "atari",
                        "sega",
                        "nintendo",
                        "x[ -]?box",
                        "transistor",
                        "dab",
                        "vhs",
                        "vcr",
                        "pvr",
                        "video",
                        "ps[ -]?[1-9]",
                    ]
                ),
            ],
        }
    )

    topics = topics.with_columns(
        rx=pl.col("patt").map_elements(lambda x: re.compile(x), return_dtype=pl.Object)
    )

    df = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
    itemtypes = get_item_types(df)
    for row in topics.iter_rows():
        topic = row[0]
        rx = row[1]
        logger.debug("*** {} ***".format(topic))
        logger.debug(rx)
        matched = []
        for item in itemtypes.iter_rows():
            item_type = item[1]
            matches = rx.search(item_type)
            if matches != None:
                logger.debug(matches.group())
                matched.append(item_type)

        pattern = "|".join(list(set(matched)))
        logger.debug(pattern)
        results = df.filter(pl.col("partner_product_category").str.contains(pattern))
        results.write_csv(f"{cfg.OUT_DIR}/ords_regex_topic_{topic}.csv")
