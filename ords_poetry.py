#!/usr/bin/env python3

from funcs import *
import pandas as pd
import os
logger = logfuncs.init_logger(__file__)

# Challenge - build a Repair Haiku generator.

# Read the data file as type string with na values set to empty string.
df = pd.read_csv(pathfuncs.path_to_ords_csv(), dtype=str,
                 keep_default_na=False, na_values="")
df.dropna(axis='rows', subset=[
    'problem'], inplace=True, ignore_index=True)
# Language by country code is not guaranteed but mostly works.
# 'GBR', 'USA', 'DEU', 'NLD', 'BEL', 'FRA'
df = df[df['country'].isin(['GBR', 'USA'])]
# Filter for shorter strings in the `problem` column.
df = df[(df['problem'].apply(lambda s: len(str(s)) < 32))]
# Filter for unique strings.
df.drop_duplicates(subset=['problem'], inplace=True)

os.system('clear')
verses = 12
lines = 5
for n in range(verses):
    rows = df.sample(n=lines)
    for i in range(0, len(rows)):
        print(rows.iloc[i].problem)
        logger.debug(rows.iloc[i].problem)
    print('')
    logger.debug('')
