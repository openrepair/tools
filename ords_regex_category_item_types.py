#!/usr/bin/env python3

# Compile a table of common item types using multi-lingual regular expressions.

import re
import polars as pl
from funcs import *


# Return regex matching information for a given term.
def get_matches(category, row, rx):
    if rx:
        matches = rx.search(row[0])
        if matches:
            return [category, row[0], row[1], matches.group()]
    return False


# Split the partner_product_category string.
def get_item_types():

    df = ordsfuncs.get_data(envfuncs.get_var("ORDS_DATA"))
    data = (
        df.with_columns(
            pl.col("partner_product_category")
            .str.split("~")
            .list.last()
            .str.strip_chars_start()
            .alias("item_type")
        )
        .select(pl.col("product_category", "item_type"))
        .drop_nulls()
        .group_by("product_category", "item_type")
        .len("records")
    )

    return data


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    rexes = pl.read_csv(ordsfuncs.DATA_DIR + "/product_category_regexes.csv")

    # Pre-compile the regexes
    rexes = rexes.with_columns(
        obj=pl.col("regex").map_elements(
            lambda x: re.compile(x, re.I), return_dtype=pl.Object
        )
    )

    # Changes to the ORDS categories will require updates to the regexes.
    categories = ordsfuncs.get_categories(envfuncs.get_var("ORDS_CATS"))

    itemtypes = get_item_types()
    results = []
    for id, category in categories.iter_rows():

        logger.debug("*** {} ***".format(category))
        print("*** {} ***".format(category))

        regex = rexes.filter((pl.col("product_category") == category)).select(
            pl.col("obj")
        )
        if regex.height != 1:
            continue

        rx = regex["obj"].item()

        terms = itemtypes.filter((pl.col("product_category") == category)).select(
            pl.col("item_type", "records")
        )

        for row in terms.iter_rows():
            matches = get_matches(category, row, rx)
            if matches:
                results.append(matches)

    results = pl.DataFrame(
        data=results,
        schema={
            "product_category": pl.String,
            "item_type": pl.String,
            "records": pl.Int64,
            "match": pl.String,
        },
    )
    results.write_csv(ordsfuncs.OUT_DIR + "/ords_regex_category_item_types.csv")
