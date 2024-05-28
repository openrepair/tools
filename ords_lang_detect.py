#!/usr/bin/env python3

# Detect languages in ORDS data using the Python langdetect package.

# https://github.com/Mimino666/langdetect
# This library is a direct port of Google's language-detection library from Java to Python. All the classes and methods are unchanged, so for more information see the project's website or wiki.
# Presentation of the language detection algorithm: http://www.slideshare.net/shuyo/language-detection-library-for-java.
# https://code.google.com/archive/p/language-detection/wikis/Tools.wiki


from langdetect import detect
from langdetect import DetectorFactory
import polars as pl
from funcs import *


if __name__ == "__main__":

    logger = cfg.init_logger(__file__)

    DetectorFactory.seed = 0

    data = (
        ordsfuncs.get_data(cfg.get_envvar("ORDS_DATA"))
        .drop_nulls(subset="problem")
    )
    data = data.filter(pl.col("problem").str.len_chars() > 64).sample(10)
    logger.debug(data)
    data = data.with_columns(language=pl.col("problem").map_elements(
            lambda p: detect(p), return_dtype=pl.String
        ))
    logger.debug(data)
    data.write_csv(cfg.OUT_DIR + "/ords_lang_detect.csv")
