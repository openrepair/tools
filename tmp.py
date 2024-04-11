#!/usr/bin/env python3

from funcs import *
import re
import pandas as pd
import time



def slice_item_types():
    tablename = envfuncs.get_var('ORDS_DATA')
    sql = """
    SELECT
    t1.product_category,
    t1.item_type,
    COUNT(*) as records
    FROM (
    SELECT
    product_category,
    TRIM(IF(INSTR(partner_product_category, '~'),
    SUBSTRING_INDEX(partner_product_category, '~', -1),
    partner_product_category)) as item_type
    FROM `{}`
    ) t1
    GROUP BY product_category, item_type
    ORDER BY product_category, records DESC
    """.format(tablename)

    start = time.time()
    dbfuncs.query_fetchall(sql)
    end = time.time()
    print(end - start)

slice_item_types()
exit()

lines = ["foo.", "bar.",]
df = pd.DataFrame(data = lines, columns = ["line"])
print(df)
df["line"].str.strip(".")
print(df)
df["line"] = df["line"].str.strip(".")
print(df)
exit()

patt = r"(?i)^(([0-9]+)?\.?[0-9\s]+kg\.?)$"

lines = [
"6kg.",
"1 kg",
"0.2kg",
"0.2 kg",
"0.1 kg.",
"9.211kg.",
"9.33 kg",]

df = pd.DataFrame(data = lines, columns = ["line"])
df.replace(
    {"line": r"(?i)^(([0-9]+)?\.?[0-9\s]+kg\.?)$"},
    {"line": "foo"},
    regex=True,
    inplace=True,
)
print(df)
exit()

for line in lines:
    foo = re.search(patt, line)
    if foo != None:
        print(foo.group(0))

    foo = re.match(patt, line)
    if foo != None:
        print(foo.group(0))

    foo = re.sub(patt, 'foo', line)
    if foo != None:
        print(foo)



exit()