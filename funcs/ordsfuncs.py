import os
import polars as pl

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(ROOT_DIR, "log", "")
DATA_DIR = os.path.join(ROOT_DIR, "dat", "")
OUT_DIR = os.path.join(ROOT_DIR, "out", "")


if not os.path.exists("dat"):
    os.mkdir("dat")
if not os.path.exists("log"):
    os.mkdir("log")
if not os.path.exists("out"):
    os.mkdir("out")


def csv_path(filename):

    return "dat/ords/" + filename + ".csv"


def get_data(filename):

    return pl.read_csv(
        csv_path(filename),
        try_parse_dates=True,
        dtypes=polars_schema(),
        infer_schema_length=0,
        ignore_errors=True,
        missing_utf8_is_empty_string=True,
    )


def polars_schema():

    return {
        "product_category_id": pl.Int64,
        "year_of_manufacture": pl.Int64,
        "product_age": pl.Float64,
        "group_identifier": pl.String,
        "repair_barrier_if_end_of_life": pl.String,
        "event_date": pl.Date,
    }


def get_categories(filename):

    return pl.read_csv(
        csv_path(filename),
        dtypes={
            "product_category_id": pl.Int64,
            "product_category": pl.String,
        },
    )
