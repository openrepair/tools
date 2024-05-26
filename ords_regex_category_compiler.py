#!/usr/bin/env python3


# Given a list of "terms" (actually mini-regexes), return a whole regular expression string for each category.


import polars as pl
import re
from funcs import *

if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    testterms = pl.read_csv(ordsfuncs.DATA_DIR + "/ords_testdata_common_products.csv")
    rxelems = pl.read_csv(ordsfuncs.DATA_DIR + "/product_category_regex_elements.csv")

    regs = []
    for category in rxelems.columns:
        print(category)
        logger.debug(category)
        data = rxelems.select(pl.col(category)).drop_nulls()
        logger.debug(data[category])
        regex = miscfuncs.build_regex_string(data[category])
        regs.append(regex)
        rx = re.compile(regex)
        tests = testterms.filter(pl.col("product_category") == category)
        for cat, prod in tests.iter_rows():
            logger.debug(prod)
            matches = rx.search(prod)
            logger.debug(matches)
    results = pl.DataFrame(
        data={
            "product_category": rxelems.columns,
            "lang": ["any"] * len(rxelems.columns),
            "regex": regs,
        },
        schema={"product_category": pl.String, "lang": pl.String, "regex": pl.String},
    )
    logger.debug(results)
    results.write_csv(ordsfuncs.OUT_DIR + "/product_category_regexes.csv")
