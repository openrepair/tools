#!/usr/bin/env python3


"""
Values in the product_age and year_of_manufacture columns are not always correct.
Often a seemingly impossible product age can mean a vintage or antique device.
Sometimes a value is simply an input error.
See the "How" story in the [data/README.md](data/README.md) about data collection.
Every effort is made to tidy up mistakes at source but it is an ongoing task.
This code can find outliers using a timeline of consumer electronics.
To truly verify an outlier it is necessary to look at the item type, brand and problem.
This script also flags vintage, antique and recent devices.
"""

import polars as pl
import datetime
from datetime import datetime
from funcs import *


def get_data():

    df = ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
    df = (
        df.drop_nulls(subset=["year_of_manufacture"])
        .filter(
            pl.col("product_category") != pl.lit("Misc"),
        )
        .select(
            pl.col(
                "id",
                "year_of_manufacture",
                "product_age",
                "event_date",
                "product_category",
                "product_category_id",
                "brand",
                "partner_product_category",
                "problem",
            )
        )
        .with_columns(
            pl.col("partner_product_category")
            .str.split("~")
            .list.last()
            .str.strip_chars()
            .alias("item_type")
        )
    ).drop_nulls(subset=["item_type"])
    return df


# Assumptions that can be changed.
# 1. vintage cut-off is halfway between current year minus earliest year
# 2. recent year is between current year and 10 years previous
def process_age_data(data):

    dt = {
        "year_curr": pl.Int64,
        "year_event": pl.Int64,
        "year_recent": pl.Int64,
        "year_vintage": pl.Int64,
        "year_decade": pl.Int64,
        "is_impossible": pl.Boolean,
        "is_mistake": pl.Boolean,
        "is_vintage": pl.Boolean,
        "is_antique": pl.Boolean,
        "is_recent": pl.Boolean,
    }
    try:
        curr_year = datetime.now().year
        data = data.with_columns(
            year_curr=pl.lit(curr_year).cast(pl.Int64),
            year_recent=pl.lit(curr_year - 10).cast(pl.Int64),
            year_event=pl.col("event_date").cast(pl.Date).dt.year().cast(pl.Int64),
            year_decade=pl.col("year_of_manufacture")
            .cast(pl.String)
            .str.replace(r"([\d]{3})([0-9])", "${1}0")
            .cast(pl.Int64),
            year_vintage=(
                pl.lit(curr_year) - ((pl.lit(curr_year) - pl.col("earliest")) / 2)
            ).cast(pl.Int64),
        )
        data = data.with_columns(
            is_mistake=pl.col("year_of_manufacture") >= pl.col("year_event"),
            is_impossible=(pl.col("year_of_manufacture") <= pl.col("earliest"))
            & (pl.col("year_of_manufacture") > pl.col("year_curr")),
            is_recent=pl.col("year_of_manufacture") >= pl.col("year_recent"),
            is_antique=pl.col("year_of_manufacture") <= pl.col("year_vintage"),
            is_vintage=(pl.col("year_of_manufacture") >= pl.col("year_vintage"))
            & (pl.col("year_of_manufacture") <= pl.col("year_recent")),
        )

    except Exception as error:
        print(error)
    return data


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    # Read the timeline data.
    df_ref = pl.read_csv(
        f"{cfg.DATA_DIR}/consumer_electronics_timeline.csv"
    ).drop_nulls(subset=["earliest"])

    # Read the ORDS data.
    df_in = get_data()

    # Join the two frames.
    data = df_in.join(df_ref, on="product_category_id", how="left")

    df_out = process_age_data(data)

    df_1 = df_out.filter(
        (pl.col("is_vintage") == True) | (pl.col("is_antique") == True)
    ).sort("product_category")
    df_1.write_csv(f"{cfg.OUT_DIR}/{cfg.get_envvar('ORDS_DATA')}_product_ages_vintage.csv")

    df_2 = df_out.filter(
        (pl.col("is_impossible") == True) | (pl.col("is_mistake") == True)
    ).sort("product_category")
    df_2.write_csv(f"{cfg.OUT_DIR}/{cfg.get_envvar('ORDS_DATA')}_product_ages_impossible.csv")