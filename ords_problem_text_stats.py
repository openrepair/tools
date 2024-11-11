import polars as pl
from funcs import *

# Basic data quality check on the `problem` text field.
# Looking for empty and short strings.

def stats(dp=None):

    df_all = (
        ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
        .select(
            [
                "id",
                "data_provider",
                "product_category",
                "repair_status",
                "event_date",
                "problem",
            ]
        )
        .with_columns(year=pl.col("event_date").str.to_date().dt.year())
    )
    if dp != None:
        logger.debug(f"*** {dp} *** ")
        df_all = df_all.filter(pl.col("data_provider") == pl.lit(dp))

    df_years = (
        df_all.group_by("year", "data_provider")
        .len("total")
        .select(["year", "data_provider", "total"])
        .sort(by=["year", "data_provider"])
    )
    df_empty = (
        df_all.filter(pl.col("problem") == "")
        .group_by("year", "data_provider")
        .len("empty")
        .select(["year", "data_provider", "empty"])
        .sort(by=["year", "data_provider"])
    )
    df_short = (
        df_all.filter(pl.col("problem").str.len_chars().is_between(1, 63))
        .group_by("year", "data_provider")
        .len("lt_64")
        .select(["year", "data_provider", "lt_64"])
        .sort(by=["year", "data_provider"])
    )

    df = df_years.join(df_empty, on=["year", "data_provider"], how="left").join(
        df_short, on=["year", "data_provider"], how="left"
    )
    df = (
        df.with_columns(
            ((pl.col("empty") / pl.col("total")).round(4) * 100)
            .fill_null(strategy="zero")
            .alias("% empty"),
            ((pl.col("lt_64") / pl.col("total")).round(4) * 100)
            .fill_null(strategy="zero")
            .alias("% < 64 chars"),
        )
        .select(["data_provider", "year", "total", "% empty", "% < 64 chars"])
        .rename({"year": "event year", "total": "records"})
    )
    logger.debug(df)


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    providers = ordsfuncs.get_data_providers()

    for prov in providers:
        stats(prov)
