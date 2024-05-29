#!/usr/bin/env python3

# Test compiled regular expressions agains a list of common item types.

import re
import polars as pl
from funcs import *


# Just a little debug helper.
def log_info(category, lang, term):
    logger.debug(f"*** {category} {lang} {term} ***")
    print(f"*** {category} {lang} {term} ***")


# Return regex matching information for a given term.
def get_matches(category, term, lang, rx):
    match = ""
    if rx:
        matches = rx.search(term)
        if matches:
            match = matches.group()
        result = [category, term, lang, bool(match), match]
    else:
        result = [category, term, lang, False, "no regex"]
    return result


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    rexes = pl.read_csv(f"{cfg.DATA_DIR}/product_category_regexes.csv")

    # Pre-compile the regexes
    rexes = rexes.with_columns(
        obj=pl.col("regex").map_elements(
            lambda x: re.compile(x, re.I), return_dtype=pl.Object
        )
    )

    # Changes to the ORDS categories will require updates to the regexes.
    categories = ordsfuncs.get_categories(cfg.get_envvar("ORDS_CATS"))

    # A set of real-world product term translations.
    allterms = pl.read_csv(
        f"{cfg.DATA_DIR}/ords_testdata_multilingual_products.csv"
    )
    langs = ["en", "nl", "fr", "de"]
    results = []
    for id, category in categories.iter_rows():

        regex = rexes.filter((pl.col("product_category") == category)).select(
            pl.col("obj")
        )
        if regex.height != 1:
            continue

        rx = regex["obj"].item()

        for lang in langs:

            terms = allterms.filter((pl.col("product_category") == category)).select(
                pl.col(lang)
            )
            for term in terms.iter_rows():
                log_info(category, lang, term[0])
                matches = get_matches(category, term[0], lang, rx)
                results.append(matches)

    results = pl.DataFrame(
        data=results,
        schema={
            "product_category": pl.String,
            "term": pl.String,
            "lang": pl.String,
            "matched": pl.Boolean,
            "match": pl.String,
        },
    )

    results.write_csv(f"{cfg.OUT_DIR}/product_category_regex_test_results.csv")
