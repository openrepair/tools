# import pandas as pd
# from funcs import pathfuncs
# from funcs import envfuncs
# from funcs import textfuncs
import os
import re
import polars as pl

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(ROOT_DIR, "log", "")
DATA_DIR = os.path.join(ROOT_DIR, "dat", "")
WEB_DIR = os.path.join(ROOT_DIR, "web", "")
OUT_DIR = os.path.join(ROOT_DIR, "out", "")


if not os.path.exists("dat"):
    os.mkdir("dat")
if not os.path.exists("log"):
    os.mkdir("log")
if not os.path.exists("web"):
    os.mkdir("web")
if not os.path.exists("out"):
    os.mkdir("out")


def get_envvars():
    pathvars = {}
    rex = re.compile(r"^PATH_TO_([_A-Z]+)")
    for key in os.environ.keys():
        matched = rex.search(key)
        if matched != None:
            pathvars[matched.group(1)] = os.environ[key]
    return pathvars


pathvars = get_envvars()


def csv_path(filename):

    return "dat/ords/" + filename + ".csv"


def polars_schema():

    return {
        "product_category_id": pl.Int64,
        "year_of_manufacture": pl.Int64,
        "product_age": pl.Float64,
        "group_identifier": pl.String,
        "repair_barrier_if_end_of_life": pl.String,
        "event_date": pl.Date,
    }


def get_data(csvfile):

    return pl.read_csv(
        csvfile,
        try_parse_dates=True,
        dtypes=polars_schema(),
        infer_schema_length=0,
        ignore_errors=True,
        missing_utf8_is_empty_string=True,
    )


# def get_non_empty_problem_list(max=0, length=0, category=None, language="en"):

#     df = get_ords_data_enriched(lang=language)
#     if category != None:
#         df = df[(df["product_category"] == category)]
#     df = textfuncs.clean_text(df)
#     df = df[(df["problem"].apply(lambda s: len(str(s)) > length))]
#     if max > 0:
#         df = df.iloc[0:max]
#     return list(df["problem"])


# def get_ords_data(index="id", lang=None, dropEmptyProblem=False):

#     path = pathfuncs.get_path(
#         [pathfuncs.ORDS_DIR, envfuncs.get_var("ORDS_DATA") + ".csv"]
#     )
#     df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values="")
#     df.set_index(index, inplace=True)
#     return df


# def get_ords_data_enriched(index="id", lang=None, dropEmptyProblem=False):

#     path = pathfuncs.get_path([pathfuncs.OUT_DIR, "ords_rich.csv"])
#     df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values="")
#     df.set_index(index, inplace=True)
#     if lang != None:
#         df = df.loc[df["language"] == "en"]
#     if dropEmptyProblem:
#         df["problem"].replace("", None, inplace=True)
#         df.dropna(subset=["problem"], inplace=True)
#     return df


# def get_ords_categories():

#     return pd.read_csv(
#         pathfuncs.get_path([pathfuncs.ORDS_DIR, envfuncs.get_var("ORDS_CATS") + ".csv"])
#     )


# def get_ords_translations():

#     df = pd.read_csv(
#         pathfuncs.get_path([pathfuncs.DATA_DIR, "ords_problem_translations.csv"])
#     )
#     df.set_index("id_ords", inplace=True)
#     return df


# def get_ords_table_schemas():

#     import json

#     path = pathfuncs.get_path([pathfuncs.ORDS_DIR, 'tableschema.json'])
#     if not pathfuncs.check_path(path):
#         print('File not found! {}'.format(path))
#         return False
#     with open(path) as schema_file:
#         content = schema_file.read()

#     parsed = json.loads(content)
#     tables = parsed['resources']
#     result = {}
#     for table in tables:
#         result[pathfuncs.get_filestem(table['path'])] = {
#             'pkey': table['schema']['primaryKey'],
#             'fields':  table['schema']['fields']}

#     return result
