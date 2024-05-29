import polars as pl
from funcs import cfg


def csv_path_ords(filename):

    return f"{cfg.ORDS_DIR}/{filename}.csv"


def csv_path_quests(filepath):

    return f"{cfg.DATA_DIR}/quests/{filepath}.csv"


def get_data(filename):

    return pl.read_csv(
        csv_path_ords(filename),
        schema=polars_schema(),
        ignore_errors=True,
        # missing_utf8_is_empty_string=True,
        try_parse_dates=True,
    )


def polars_schema():
    return {
        "id": pl.String,
        "data_provider": pl.String,
        "country": pl.String,
        "partner_product_category": pl.String,
        "product_category": pl.String,
        "product_category_id": pl.Int64,
        "brand": pl.String,
        "year_of_manufacture": pl.Int64,
        "product_age": pl.Float64,
        "repair_status": pl.String,
        "repair_barrier_if_end_of_life": pl.String,
        "group_identifier": pl.String,
        "event_date": pl.String,
        "problem": pl.String,
    }


def get_categories(filename):

    return pl.read_csv(
        csv_path_ords(filename),
        schema={
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
        .str.strip_chars()
        .alias("product")
    )


def table_schemas():

    from funcs import pathfuncs
    import json

    path = cfg.ORDS_DIR + "/tableschema.json"
    if not pathfuncs.check_path(path):
        print(f"File not found! {path}")
        return False
    with open(path) as schema_file:
        content = schema_file.read()

    parsed = json.loads(content)
    tables = parsed["resources"]
    result = {}
    for table in tables:
        result[pathfuncs.get_filestem(table["path"])] = {
            "pkey": table["schema"]["primaryKey"],
            "fields": table["schema"]["fields"],
        }

    return result
