#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re


def get_data():

    df = pd.read_csv(
        pathfuncs.path_to_ords_csv(), dtype=str, keep_default_na=False, na_values=""
    )
    logger.debug("TOTAL ORDS RECORDS: {}".format(len(df)))
    df = df.reindex(columns=["product_category", "partner_product_category"])
    df.rename(columns={"partner_product_category": "item_type"}, inplace=True)
    logger.debug(
        "TOTAL EMPTY ITEM TYPES: {}".format(len(df.loc[df["item_type"] == ""]))
    )
    df["item_type"] = df["item_type"].apply(lambda s: s.split("~").pop().strip())
    df = (
        df.groupby(["product_category", "item_type"])
        .size()
        .reset_index(name="records")
        .sort_values(["product_category", "records"], ascending=[True, False])
    )
    df["matched"] = 0
    df["unu_keys"] = ""
    df["products"] = ""
    logger.debug("TOTAL NON-EMPTY UNIQUE ITEM TYPES: {}".format(len(df)))

    return df


# Given a list of "terms" (actually mini-regexes), return a compiled regex for each product.
def build_regexes():

    rxelems = pd.read_csv(pathfuncs.DATA_DIR + "/product_regexes.csv", dtype=str)
    regexes = {}
    regexes = regexes.fromkeys(rxelems.columns)
    for key in regexes:
        pattern = miscfuncs.build_regex_string(rxelems[key].dropna().values)
        regexes[key] = re.compile(pattern, flags=re.IGNORECASE + re.UNICODE)

    return regexes


# product,ords_product_category,unu_key,unu_id,ords_id
def run_regexes(regexes, data):

    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map.csv", dtype=str)
    result = {}
    result = result.fromkeys(map["unu_id"])
    for n, row in map.iterrows():
        terms = data.loc[data["product_category"] == row["ords_product_category"]]
        key = row["unu_id"]
        rx = regexes[row["product"]]
        for i, term in terms.iterrows():
            matches = rx.search(term["item_type"])
            if matches != None:
                keys = data.at[i, "unu_keys"].split(",")
                keys.append(key)
                keys = list(set(list(filter(None, keys))))
                data.at[i, "matched"] = len(keys)
                data.at[i, "unu_keys"] = ",".join(keys)

                prods = data.at[i, "products"].split(",")
                prods.append(row["product"])
                data.at[i, "products"] = ",".join(list(filter(None, prods)))

    return data


# product,ords_product_category,unu_key,unu_id,ords_id
def run_regexes_misc(regexes, data):

    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map.csv", dtype=str)
    result = {}
    result = result.fromkeys(map["unu_id"])
    terms = data.loc[data["product_category"] == "Misc"]
    for n, row in map.iterrows():
        key = row["unu_id"]
        rx = regexes[row["product"]]
        for i, term in terms.iterrows():
            matches = rx.search(term["item_type"])
            if matches != None:
                keys = data.at[i, "unu_keys"].split(",")
                keys.append(key)
                keys = list(set(list(filter(None, keys))))
                data.at[i, "matched"] = len(keys)
                data.at[i, "unu_keys"] = ",".join(keys)

                prods = data.at[i, "products"].split(",")
                prods.append(row["product"])
                data.at[i, "products"] = ",".join(list(filter(None, prods)))

    return data


def set_defaults(data):

    for title, pair, default in subsets:
        keys = pd.read_csv(
            pathfuncs.OUT_DIR + "/unukey_matches_{}_before.csv".format(title), dtype=str
        )
        for n, row in keys.iterrows():
            data["matched"].loc[
                (data["product_category"] == row["product_category"])
                & (data["item_type"] == row["item_type"])
            ] = 1
            data["unu_keys"].loc[
                (data["product_category"] == row["product_category"])
                & (data["item_type"] == row["item_type"])
            ] = default

    # Set default keys.
    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map_default.csv", dtype=str)
    for n, row in map.iterrows():
        data["unu_keys"].loc[
            (data["product_category"] == row["product_category"])
            & (data["matched"] == 0)
        ] = row["unu_id"]

    logger.debug("ASSIGNED UNU KEYS: {}".format(len(data.loc[data["unu_keys"] > ""])))

    return data


def write_summaries(data, prefix=""):

    multi = data.loc[result["matched"] > 1]
    multi.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_multi_{}.csv".format(prefix), index=False)
    logger.debug("MULTIPLE MATCHES: {}".format(len(multi)))
    cats = (
        multi.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)

    one = data.loc[result["matched"] == 1]
    one.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_one._{}.csv".format(prefix), index=False)
    logger.debug("ONE MATCH: {}".format(len(one)))
    cats = (
        one.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )

    defaults = data.loc[(data["matched"] == 0) & (data["unu_keys"] > "")]
    defaults.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_defaults_{}.csv".format(prefix), index=False)
    logger.debug("BACKFILLED MATCHES: {}".format(len(defaults)))
    cats = (
        defaults.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)

    none = data.loc[(data["matched"] == 0) & (data["unu_keys"] == "")]
    none.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_none_{}.csv".format(prefix), index=False)
    logger.debug("NO MATCHES: {}".format(len(none)))
    cats = (
        none.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)

    for title, pair, default in subsets:
        _write_dual_match(data, pair, title, prefix)


def _write_dual_match(data, keys, title, prefix=""):

    l = keys.split(",")
    df = data.loc[
        (data["unu_keys"] == keys) | (data["unu_keys"] == "{},{}".format(l[1], l[0]))
    ]
    df.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_{}_{}.csv".format(title, prefix), index=False)
    logger.debug("*** {} matches: {} ***".format(title, len(df)))
    cats = (
        df.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)
    return cats


def assign_keys():

    df = pd.read_csv(
        pathfuncs.path_to_ords_csv(), dtype=str, keep_default_na=False, na_values=""
    )
    df["unu_key"] = ""
    df["unu_str"] = ""
    df["item_type"] = df["partner_product_category"].apply(
        lambda s: s.split("~").pop().strip()
    )

    keys = pd.read_csv(pathfuncs.OUT_DIR + "/unukey_matches_defaults.csv", dtype=str)
    for n, row in keys.iterrows():
        df["unu_key"].loc[
            (df["product_category"] == row["product_category"])
            & (df["item_type"] == row["item_type"])
        ] = row["unu_keys"]

    keys = pd.read_csv(pathfuncs.OUT_DIR + "/unukey_matches_one.csv", dtype=str)
    for n, row in keys.iterrows():
        df["unu_key"].loc[
            (df["product_category"] == row["product_category"])
            & (df["item_type"] == row["item_type"])
        ] = row["unu_keys"]
    logger.debug("ASSIGNED UNU KEYS: {}".format(len(df.loc[df["unu_key"] > ""])))

    keys = pd.read_csv(pathfuncs.DATA_DIR + "/unu_keys.csv", dtype=str)
    for n, row in keys.iterrows():
        df["unu_str"].loc[(df["unu_key"] == row["key"])] = row["description"]

    return df


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    logger.debug("BEFORE DEFAULTS")
    regexes = build_regexes()
    data = get_data()
    result = run_regexes(regexes, data)
    # Run all regexes against the Misc category.
    result = run_regexes_misc(regexes, data)
    # Some UNU cats are subsets of ORDS cats, e.g. lighting and LED lighting, Hi-Fi and speakers etc.
    subsets = [
        ["lights", "505,501", "505"],
        ["screens", "309,408", "408"],
        ["speakers", "405,403", "405"],
        ["heaters", "106,201", "106"],
        ["remotes", "201,401", "401"],
        ["aircon", "111,112", "112"],
        ["cooker", "202,203", "203"],
        ["scales", "801,201", "201"],
        ["mwave", "114,703", "114"], # todo: fix exercise regex to exlude "microgolfoven"
    ]
    write_summaries(result, prefix="before")
    result = set_defaults(result)
    logger.debug("AFTER DEFAULTS")
    write_summaries(result, prefix="after")
    exit()
    data = assign_keys()
    data.to_csv(pathfuncs.OUT_DIR + "/unukey_matched_data.csv", index=False)
