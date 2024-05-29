#!/usr/bin/env python3


# Slices the data to produce useful subsets for, e.g., data viz.
# Writes the dataframes to csv and json format files.


import datetime
import polars as pl
from funcs import *


# Events date range sorted by event_date.
def slice_events(df):

    dfsub = (
        df.filter(
            pl.col("event_date").is_between(
                datetime.date(2018, 1, 1), datetime.date(2021, 12, 31)
            ),
        )
        .select(
            pl.col("id", "data_provider", "event_date", "group_identifier", "country")
        )
        .sort("event_date")
    )
    logger.debug(dfsub)
    write_to_files(dfsub, "events")


# Products and repairs sorted by product_age.
def slice_repairs(df):

    dfsub = (
        df.filter(
            pl.col("product_age").is_not_null(),
        )
        .select(
            pl.col(
                "id",
                "product_age",
                "year_of_manufacture",
                "repair_status",
                "repair_barrier_if_end_of_life",
            )
        )
        .sort("product_age")
    )

    logger.debug(dfsub)
    write_to_files(dfsub, "repairs")


# Product age.
def slice_product_age(df):

    dfsub = df.filter(
        pl.col("product_age").is_not_null(),
    ).select(
        pl.col(
            "product_category",
            "product_age",
        )
    )
    dfsub = (
        dfsub.group_by(["product_category"])
        .agg(
            pl.col("product_age").min().alias("earliest"),
            pl.col("product_age").max().alias("latest"),
            pl.col("product_age").mean().alias("average"),
        )
        .sort("product_category")
    )
    logger.debug(dfsub)
    write_to_files(dfsub, "product_age")


# Year of manufacture.
def slice_year_of_manufacture(df):

    dfsub = df.filter(
        pl.col("year_of_manufacture").is_not_null(),
    ).select(
        pl.col(
            "product_category",
            "year_of_manufacture",
        )
    )
    dfsub = (
        dfsub.group_by(["product_category"])
        .agg(
            pl.col("year_of_manufacture").min().alias("newest"),
            pl.col("year_of_manufacture").max().alias("oldest"),
            pl.col("year_of_manufacture").mean().cast(pl.Int32).alias("average"),
        )
        .sort("product_category")
    )
    logger.debug(dfsub)
    write_to_files(dfsub, "year_of_manufacture")


# Product categories sorted by product_category.
def slice_categories(df):

    dfsub = df.select(
        pl.col(
            "id",
            "partner_product_category",
            "product_category",
            "repair_status",
        )
    ).sort("product_category", "partner_product_category")
    logger.debug(dfsub)
    write_to_files(dfsub, "categories")


# Item types split from partner_product_category string.
def slice_item_types(df):

    dfsub = df.select(
        pl.col(
            "product_category",
            "partner_product_category",
        )
    )
    dfsub = dfsub.with_columns(
        pl.col("partner_product_category")
        .str.split(" ~ ")
        .list.tail(1)
        .list.join("")
        .alias("item_type")
    )
    dfsub = (
        dfsub.group_by(["product_category", "item_type"])
        .agg(
            pl.col("item_type").count().name.suffix("_count"),
        )
        .sort(
            "product_category",
            "item_type_count",
            "item_type",
            descending=[False, True, False],
        )
    )
    logger.debug(dfsub)
    write_to_files(dfsub, "item_types")


# Countries and groups.
def slice_countries(df):

    countries = pl.read_csv(f"{cfg.DATA_DIR}/iso_country_codes.csv").sort("iso")
    logger.debug(countries)
    dfsub = (
        df.select(
            pl.col(
                "group_identifier",
                "country",
            )
        )
        .rename({"country": "iso", "group_identifier": "group"})
        .sort("iso")
    )
    logger.debug(dfsub)
    dfsub = dfsub.join(countries, on="iso", how="left")
    logger.debug(dfsub)
    dfsub = (
        dfsub.group_by(["iso", "group", "country"]).agg(
            pl.col("group").count().name.suffix("_count"),
        )
    ).sort("iso", "group")
    logger.debug(dfsub)
    write_to_files(dfsub, "countries")


# Set sample to a fraction to return a subset of results.
# Can be useful for testing, e.g. data visualisation.
def write_to_files(df, suffix, sample=0):

    if sample:
        df = df.sample(frac=sample, with_replacement=False)

    path = f"{cfg.OUT_DIR}/{cfg.get_envvar('ORDS_DATA')}_{suffix}"
    df.write_csv(path + ".csv")
    print(path + ".csv")
    df.write_json(path + ".json", row_oriented=True, pretty=True)
    print(path + ".json")


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    dt = {
        "product_category_id": pl.Int64,
        "year_of_manufacture": pl.Int64,
        "product_age": pl.Float64,
        "group_identifier": pl.String,
        "repair_barrier_if_end_of_life": pl.String,
        "event_date": pl.Date,
    }
    df = pl.read_csv(
        "dat/ords/" + cfg.get_envvar("ORDS_DATA") + ".csv",
        try_parse_dates=True,
        dtypes=dt,
        infer_schema_length=0,
        ignore_errors=True,
        missing_utf8_is_empty_string=True,
    )
    logger.debug(df.schema)

    slice_events(df)
    slice_repairs(df)
    slice_product_age(df)
    slice_year_of_manufacture(df)
    slice_categories(df)
    slice_item_types(df)
    slice_countries(df)
