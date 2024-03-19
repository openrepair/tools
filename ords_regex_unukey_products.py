#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re
import csv


def get_item_types():

    df = pd.read_csv(
        pathfuncs.path_to_ords_csv(), dtype=str, keep_default_na=False, na_values=""
    )
    logger.debug("TOTAL ORDS RECORDS: {}".format(len(df)))
    df = df.reindex(columns=["product_category", "partner_product_category"])
    df.rename(columns={"partner_product_category": "product"}, inplace=True)
    logger.debug("TOTAL EMPTY ITEM TYPES: {}".format(len(df.loc[df["product"] == ""])))
    df["product"] = df["product"].apply(lambda s: s.split("~").pop().strip())
    df = (
        df.groupby(["product_category", "product"])
        .size()
        .reset_index(name="records")
        .sort_values(["product_category", "records"], ascending=[True, False])
    )
    df["matched"] = 0
    df["unu_keys"] = ""
    df["products"] = ""
    df["unu_str"] = ""
    logger.debug("TOTAL NON-EMPTY UNIQUE ITEM TYPES: {}".format(len(df)))

    return df


# Given a list of "terms" (actually mini-regexes), return a compiled regex for each product.
def build_regexes():

    rxelems = pd.read_csv(pathfuncs.DATA_DIR + "/product_regexes.csv", dtype=str)
    built = {}
    regexes = {}
    regexes = regexes.fromkeys(rxelems.columns)
    for key in regexes:
        pattern = miscfuncs.build_regex_string(rxelems[key].dropna().values)
        built[key] = pattern
        regexes[key] = re.compile(pattern, flags=re.IGNORECASE)

    out = open(pathfuncs.OUT_DIR + "/product_regexes_built.csv", "w")
    z = csv.writer(out)
    for new_k, new_v in built.items():
        z.writerow([new_k, new_v])
    out.close()
    return regexes


# product,product_category,unu_key,unu_id,ords_id
def run_regexes(regexes, data):

    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map.csv", dtype=str)
    result = {}
    result = result.fromkeys(map["unu_key"])
    x = 0
    for n, row in map.iterrows():
        terms = data.loc[data["product_category"] == row["product_category"]]
        key = row["unu_key"]
        rx = regexes[row["product"]]
        for i, term in terms.iterrows():
            matches = rx.search(term["product"])
            if matches != None:
                x += 1
                keys = data.at[i, "unu_keys"].split(",")
                keys.append(key)
                keys = list(set(list(filter(None, keys))))
                data.at[i, "matched"] = len(keys)
                data.at[i, "unu_keys"] = ",".join(keys)

                prods = data.at[i, "products"].split(",")
                prods.append(row["product"])
                data.at[i, "products"] = ",".join(list(filter(None, prods)))
        logger.debug(
            "MATCHES FOR {} ~ {} : {} ".format(
                row["product_category"], row["product"], x
            )
        )
    return data


# product,product_category,unu_key,unu_id,ords_id
def run_regexes_misc(regexes, data):

    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map.csv", dtype=str)
    result = {}
    result = result.fromkeys(map["unu_key"])
    terms = data.loc[data["product_category"] == "Misc"]
    for n, row in map.iterrows():
        key = row["unu_key"]
        rx = regexes[row["product"]]
        for i, term in terms.iterrows():
            matches = rx.search(term["product"])
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

    subsets = get_subsets()
    for title, pair, default in subsets:
        keys = pd.read_csv(
            pathfuncs.OUT_DIR + "/unukey_matches_{}_before.csv".format(title), dtype=str
        )
        for n, row in keys.iterrows():
            data["matched"].loc[
                (data["product_category"] == row["product_category"])
                & (data["product"] == row["product"])
            ] = 1
            data["unu_keys"].loc[
                (data["product_category"] == row["product_category"])
                & (data["product"] == row["product"])
            ] = default

    # Set default keys.
    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map_default.csv", dtype=str)
    for n, row in map.iterrows():
        data["unu_keys"].loc[
            (data["product_category"] == row["product_category"])
            & (data["matched"] == 0)
        ] = row["unu_key"]

    logger.debug("ASSIGNED UNU KEYS: {}".format(len(data.loc[data["unu_keys"] > ""])))

    return data


def write_summaries(data, prefix=""):

    multi = data.loc[result["matched"] > 1]
    multi.to_csv(
        pathfuncs.OUT_DIR + "/unukey_matches_multi_{}.csv".format(prefix), index=False
    )
    logger.debug("MULTIPLE MATCHES: {}".format(len(multi)))
    cats = (
        multi.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)

    one = data.loc[result["matched"] == 1]
    one.to_csv(
        pathfuncs.OUT_DIR + "/unukey_matches_one_{}.csv".format(prefix), index=False
    )
    logger.debug("ONE MATCH: {}".format(len(one)))
    cats = (
        one.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )

    defaults = data.loc[(data["matched"] == 0) & (data["unu_keys"] > "")]
    defaults.to_csv(
        pathfuncs.OUT_DIR + "/unukey_matches_defaults_{}.csv".format(prefix),
        index=False,
    )
    logger.debug("BACKFILLED MATCHES: {}".format(len(defaults)))
    cats = (
        defaults.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)

    none = data.loc[(data["matched"] == 0) & (data["unu_keys"] == "")]
    none.to_csv(
        pathfuncs.OUT_DIR + "/unukey_matches_none_{}.csv".format(prefix), index=False
    )
    logger.debug("NO MATCHES: {}".format(len(none)))
    cats = (
        none.groupby(["product_category", "products", "unu_keys"])
        .size()
        .reset_index(name="records")
        .sort_values(["records", "product_category"], ascending=[False, True])
    )
    logger.debug(cats)

    subsets = get_subsets()
    for title, pair, default in subsets:
        _write_subset_match(data, pair, title, prefix)


def _write_subset_match(data, keys, title, prefix=""):

    l = keys.split(",")
    df = data.loc[
        (data["unu_keys"] == keys) | (data["unu_keys"] == "{},{}".format(l[1], l[0]))
    ]
    df.to_csv(
        pathfuncs.OUT_DIR + "/unukey_matches_{}_{}.csv".format(title, prefix),
        index=False,
    )
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
    df["product"] = df["partner_product_category"].apply(
        lambda s: s.split("~").pop().strip()
    )

    keys = pd.read_csv(
        pathfuncs.OUT_DIR + "/unukey_matches_final_results.csv", dtype=str
    )
    for n, row in keys.iterrows():
        df["unu_key"].loc[
            (df["product_category"] == row["product_category"])
            & (df["product"] == row["product"])
        ] = row["unu_keys"]
        df["unu_str"].loc[(df["unu_key"] == row["unu_keys"])] = row["unu_str"]

    return df


# Some UNU cats are subsets of ORDS cats
# e.g. lighting/LED lighting, Hi-Fi/speakers etc.
def get_subsets():
    return [
        ["lights", "505,501", "505"],
        ["screens", "309,408", "408"],
        ["speakers", "405,403", "405"],
        ["heaters", "106,201", "106"],
        ["remotes", "201,401", "401"],
        ["remotes", "404,401", "401"],
        ["aircon", "111,112", "112"],
        ["cooker", "202,203", "203"],
        ["scales", "801,201", "201"],
        ["phones", "306,305", "305"],
    ]


def tweak(data, regexes):
    tweaks = [
        ["Mobile", "305", "^Telephone \(not mobile or smartphone\)$"],
        ["Small home electrical", "305", regexes["telecom-wired"]],
        ["Lamp", "505", regexes["lighting-led"]],
        ["Large home electrical", "106", regexes["heater"]],
        ["DSLR/video camera", "406", regexes["camera"]],
        ["TV and gaming-related accessories", "405", regexes["speaker"]],
    ]
    for row in tweaks:
        terms = data.loc[data["product_category"] == row[0]]
        key = row[1]
        if issubclass(type(row[2]), str):
            rx = re.compile(row[2], re.IGNORECASE)
        else:
            rx = row[2]
        for i, term in terms.iterrows():
            matches = rx.search(term["product"])
            if matches != None:
                keys = data.at[i, "unu_keys"].split(",")
                keys.append(key)
                keys = list(set(list(filter(None, keys))))
                data.at[i, "matched"] = 1
                data.at[i, "unu_keys"] = key

                prods = data.at[i, "products"].split(",")
                prods.append("tweaked")
                data.at[i, "products"] = ",".join(list(filter(None, prods)))
                logger.debug("TWEAKED: {}".format(row[0]))
    return data


def leftovers(data):

    map = pd.read_csv(pathfuncs.DATA_DIR + "/product_map_leftovers.csv", dtype=str)
    for n, row in map.iterrows():
        data["unu_keys"].loc[
            (data["product_category"] == row["product_category"])
            & (data["product"] == row["product"])
        ] = row["unu_key"]
    return data


def test_regex(data, regexes):
    product_category = "Small home electrical"
    product = "heater"
    rx = regexes[product]
    terms = data.loc[data["product_category"] == product_category]
    for i, term in terms.iterrows():
        matches = rx.search(term["product"])
        if matches != None:
            terms.at[i, "matched"] = 1
            terms.at[i, "products"] = product
            data.at[i, "matched"] = 1
            data.at[i, "products"] = product
    terms.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_testA_{}.csv".format(product))
    data.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_testB_{}.csv".format(product))
    return data


if __name__ == "__main__":

    logger = logfuncs.init_logger(__file__)

    # TODO
    # Look at extending product map for regexes to run on more than one category,
    # this could help with miscats and subsets but can end up over-matching.
    # e.g. LEDs in both "Lamps" and "Decorative or safety lights"
    # e.g. landlines in "Mobile"
    # e.g. heaters in both Small/Large Home Electrical
    # See tweak() for current workaround.

    # Take the product_regexes and compile a regex for each product.
    regexes = build_regexes()

    # Take the ORDS dataset, split and group the partner_product_category into products.
    data = get_item_types()

    # Run regexes using the "product map".
    result = run_regexes(regexes, data)
    result.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_data_1.csv", index=False)

    # Run all regexes against the Misc category.
    result = run_regexes_misc(regexes, data)
    result.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_data_2.csv", index=False)

    logger.debug("BEFORE AMENDMENTS")
    # Create csv summaries of regex results in the ./out folder.
    write_summaries(result, prefix="before")

    # Assign default keys to unmatched records
    # Amend keys in subsets.
    # Plus a few leftovers not caught in any of the maps and tweaks.
    # Just need to ensure that each product ends up with only one unu_key.
    result = set_defaults(result)
    result.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_data_3.csv", index=False)
    result = tweak(result, regexes)
    result = leftovers(result)

    # Values of `matched`, `records` and `products` useful for checking the regexes.
    keys = pd.read_csv(pathfuncs.DATA_DIR + "/unu_keys.csv", dtype=str)
    for n, row in keys.iterrows():
        result["unu_str"].loc[(result["unu_keys"] == row["key"])] = row["description"]
    result.to_csv(pathfuncs.OUT_DIR + "/unukey_matches_final_results.csv", index=False)

    logger.debug("AFTER AMENDMENTS")
    # Create csv summaries of amendments and defaults in the ./out folder.
    write_summaries(result, prefix="after")

    exit()
    # Append key to each individual record in the ORDS dataset.
    data = assign_keys()
    data.to_csv(pathfuncs.OUT_DIR + "/unukey_matched_data.csv", index=False)
