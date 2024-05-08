#!/usr/bin/env python3

# Test compiled regular expressions agains a list of common item types.

from funcs import *
import re
import pandas as pd


# Just a little debug helper.
def log_info(category, lang, term):
    logger.debug("*** {} {} {} ***".format(category, lang, data.loc[i]))
    print("*** {} {} {} ***".format(category, lang, data.loc[i]))


# Fetch the regex for the given category.
def get_regex(category):
    regex = rexes.loc[(rexes.product_category == category)]
    if not regex.empty and regex.product_category.count() == 1:
        return regex.obj.iloc[0]
    return False


# Return regex matching information for a given term.
def get_matches(category, term, lang):
    match = ""
    rx = get_regex(category)
    if rx:
        matches = rx.search(term)
        if matches:
            match = matches.group()
        result = [category, term, lang, bool(match), match]
    else:
        result = [category, term, lang, False, "no regex"]
    return result


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    # Create a structure to hold results.
    mapcols = ["product_category", "term", "lang", "match", "matches"]
    results = pd.DataFrame(columns=mapcols)

    rexes = pd.read_csv(pathfuncs.DATA_DIR + "/product_category_regexes.csv")
    # There should be no empty regex strings but just in case.
    rexes.dropna(inplace=True)

    # Pre-compile the regexes
    for n in range(0, len(rexes)):
        rexes.loc[n, "obj"] = re.compile(rexes.iloc[n]["regex"], re.I)

    # Changes to the ORDS categories will require updates to the regexes.
    categories = pd.read_csv(
        pathfuncs.ORDS_DIR + "/{}.csv".format(envfuncs.get_var("ORDS_CATS"))
    )

    # A set of real-world product term translations.
    terms = pd.read_csv(pathfuncs.DATA_DIR + "/ords_testdata_multilingual_products.csv")
    langs = ["en", "nl", "fr", "de"]

    for n in range(0, len(categories)):
        category = categories.iloc[n].product_category
        for lang in langs:
            data = terms.loc[(terms.product_category == category)][lang]
            data.reset_index(drop=True, inplace=True)
            for i in range(0, len(data)):
                log_info(category, lang, data.loc[i])
                matches = get_matches(category, data.loc[i], lang)
                results.loc[len(results)] = matches

    # Write results to csv format file.
    results.to_csv(
        pathfuncs.OUT_DIR + "/product_category_regex_test_results.csv", index=False
    )
