#!/usr/bin/env python3

# This query exposes some issues with repair data, namely...
# a) categorising products
# b) estimating average weights
# c) values that change over time

import polars as pl
from funcs import *


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    tablename = cfg.get_envvar("ORDS_DATA")

    # The data file (roughly) maps categories and average weight estimates between ORDS and UNU-KEYS.
    # See dat/README.md for more details.
    weights = pl.read_csv(f"{cfg.DATA_DIR}/ords_product_category_unu_key_map.csv")

    data = (
        ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
        .filter(pl.col("repair_status") == pl.lit("Fixed"))
        .join(weights, on="product_category", how="left")
        .group_by(["product_category"])
        .agg(
            pl.col("unu_1995").sum().round(1).alias("unu_1995_total"),
            pl.col("unu_2000").sum().round(1).alias("unu_2000_total"),
            pl.col("unu_2005").sum().round(1).alias("unu_2005_total"),
            pl.col("unu_2010").sum().round(1).alias("unu_2010_total"),
            pl.col("unu_2011").sum().round(1).alias("unu_2011_total"),
            pl.col("unu_2012").sum().round(1).alias("unu_2012_total"),
        )
    ).write_csv(f"{cfg.OUT_DIR}/{tablename}_stats_unu_keys_weights.csv")
