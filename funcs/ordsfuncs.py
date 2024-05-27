import os
import polars as pl

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "dat", "")
ORDS_DIR = os.path.join(ROOT_DIR, 'dat/ords')
LOG_DIR = os.path.join(ROOT_DIR, "log", "")
OUT_DIR = os.path.join(ROOT_DIR, "out", "")


if not os.path.exists("dat"):
    os.mkdir("dat")
if (not os.path.exists('dat/ords')):
    os.mkdir('dat/ords')
if not os.path.exists("log"):
    os.mkdir("log")
if not os.path.exists("out"):
    os.mkdir("out")


def csv_path_ords(filename):

    return "{}/{}.csv".format(ORDS_DIR, filename)


def csv_path_quests(filepath):

    return "{}/quests/{}.csv".format(DATA_DIR, filepath)


def get_data(filename):

    return pl.read_csv(
        csv_path_ords(filename),
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
        csv_path_ords(filename),
        dtypes={
            "product_category_id": pl.Int64,
            "product_category": pl.String,
        },
    )


# Split the partner_product_category string.
def extract_products(df):
    return df.with_columns(
        pl.col("partner_product_category")
        .str.split("~")
        .list.last()
        .str.strip_chars_start()
        .alias("product")
    )
