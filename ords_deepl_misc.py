#!/usr/bin/env python3

from funcs import *
import pandas as pd
import re

logger = logfuncs.init_logger(__file__)

# Step 1: ords_deepl_setup.py
# Step 2: ords_deepl_fetch.py
# Step 3: ords_deepl_misc.py
# https://github.com/DeepLcom/deepl-python


def bad_detections():

    sql = """
    SELECT language_detected, COUNT(*) as records
    FROM `ords_problem_translations`
    GROUP BY language_detected
    ORDER BY records DESC
    """
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql))
    df_res.to_csv(pathfuncs.OUT_DIR + '/deepl_lang_detect.csv', index=False)

    sql = """
    SELECT *
    FROM `ords_problem_translations`
    WHERE UPPER(language_detected) NOT IN ('en', 'en-gb', 'de', 'nl', 'fr', 'it', 'es')
    """
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql))
    df_res.to_csv(pathfuncs.OUT_DIR + '/deepl_bad_detect.csv', index=False)


# This func used to recover translations from logfile after a db exception.
# Exception handling implemented, data now written on exception.
# Should no longer be required.
# If intending to use this, rename the fetched logfile first, see below.
def recover_log():

    rxReq = re.compile("'target_lang': '([-A-Z]{2,5})', 'text': '(.*)'")
    rxRes = re.compile('"detected_source_language":"([-A-Z]{2,5})","text":"(.*)"')
    rows = []
    file = open(pathfuncs.LOG_DIR + '/ords_deepl_fetch_foobar.log', "r")
    lines = file.readlines()
    file.close()
    for i in range(0,len(lines)):
        if lines[i].startswith('Request to DeepL API method=POST'):
            targetlang = ''
            sourcetext = ''
            sourcelang = ''
            translation = ''
            if lines[i+1].startswith('Request details'):
                match = rxReq.search(lines[i+1])
                if match:
                    targetlang = match.group(1).removesuffix('-GB').lower()
                    sourcetext = match.group(2)
                    print(targetlang)
                    print(sourcetext)
            else:
                print('wrong string found: Request details')

            if lines[i+4].startswith('Response details'):
                print(lines[i+4])
                match = rxRes.search(lines[i+4])
                if match:
                    sourcelang = match.group(1).removesuffix('-GB').lower()
                    translation = match.group(2)
                    print(sourcelang)
                    print(translation)
            else:
                print('wrong string found: Response details')

            rows.append([sourcelang, sourcetext, targetlang, translation])

    df = pd.DataFrame(data=rows, columns=['language_detected', 'problem', 'targetlang', 'translation'])
    langs = ["en","de","nl","fr","it","es"]
    columns = ["problem", "language_known", "translator", "language_detected"] + langs
    rows = []
    dfg = df.groupby('problem')
    for problem, group in dfg:
        row = pd.Series(index=columns)
        row['language_known'] = '??'
        row["translator"] = 'DeepL'
        row["problem"] = problem
        row["language_detected"] = group.language_detected.unique()[0]
        for lang in langs:
            row[lang] = df.loc[(df['problem'] == problem) & (df['targetlang'] == lang)].translation.values[0]
        print(row)
        rows.append(row)

    result = pd.DataFrame(data = rows, columns=columns)
    result.to_csv(pathfuncs.OUT_DIR + '/ords_deepl_parsed_foobar.csv', index=False)

# Fetch assorted language strings for Solr lang detection test.
def query_lang_strings():

    langs = ["en","de","nl","fr","it","es"]
    qry = """
(SELECT
GROUP_CONCAT(DISTINCT id_ords) as id,
{fld} as problem,
'{fld}' as lang_known
FROM `ords_problem_translations`
WHERE language_known = '{fld}'
AND LENGTH(problem) > 12
GROUP BY {fld}
LIMIT {max} )
"""
    sql = ''
    print(len(langs))
    for i in range(0, len(langs)):
        sql = sql + qry.format(fld=langs[i], max=10)
        print(i)
        if i != len(langs)-1:
            sql = sql + "UNION"
    print(sql)
    df_res = pd.DataFrame(dbfuncs.query_fetchall(sql)) #, {'max': 10}))
    df_res.to_csv(pathfuncs.OUT_DIR + '/test_lang_detect_small.csv', index=False)

# START

bad_detections()
