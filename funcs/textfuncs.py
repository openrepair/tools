import re
import polars as pl


# Put together an "OR" regex string pattern from a list of lowercase terms.
# With optional prefix/suffix captures of minimum length multilingual words.
def build_regex_string(terms, pre=True, aft=True):
    result = "(?i)("
    if pre == True:
        result += "([a-zß-ÿœ]{3,}[ -]?)?"
    if len(terms) > 0:
        result += "(" + "|".join(list(set(terms))) + ")"
    if aft == True:
        result += "([a-zß-ÿœ]{3,}[ -]?)?"
    result += ")"
    return result


def clean_text(df, column="problem", dropna=True, strip=True, dedupe=True):

    df = clean_text_sentences(df, column)

    df = clean_text_html_tags(df, column)

    df = clean_text_html_symbols(df, column)

    df = clean_text_weights(df, column)

    df = clean_text_code_prefixes(df, column)

    df = clean_text_nonprinting_chars(df, column)

    df = clean_text_missing_newline(df, column)

    df = clean_text_tabs_spaces(df, column)

    if strip:
        # Trim whitespace.
        df = df.with_columns(pl.col(column).str.strip_chars())

    if dropna:
        # Drop `problem` values that may be empty after the replacements and trimming.
        df = df.filter(pl.col(column) != "").drop_nulls(subset=[column])

    if dedupe:
        # Dedupe the column values.
        df = df.unique()

    return df


# Make sure there is always a space after a period, else sentences won't be split.
def clean_text_sentences(df, column="problem"):

    p = r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"
    s = "${2}. ${3}"
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Remove HTML symbols (&gt; features a lot)
def clean_text_html_symbols(df, column="problem"):

    p = r"(?i)(&[\w\s]+;)"
    s = ""
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Remove HTML tags
def clean_text_html_tags(df, column="problem"):

    p = r"<[^>]+>"
    s = ""
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Remove weight values (0.5kg, 5kg, 5 kg, .5kg etc.)
def clean_text_weights(df, column="problem"):

    p = r"(?i)(([0-9]+)?\.?[0-9\s]+kg)"
    s = ""
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Remove random non-alpha codes often found prefixing `problem` strings.
def clean_text_code_prefixes(df, column="problem"):

    p = r"(?i)^(\W|\d+)([\d|\W]+)?"
    s = ""
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Some literal eol chars are embedded.
def clean_text_nonprinting_chars(df, column="problem"):

    p = r"(\+(r|n))"
    s = " "
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Tabs and multiple spaces.
def clean_text_tabs_spaces(df, column="problem"):

    p = r"([\s\t]+)"
    s = " "
    return df.with_columns(pl.col(column).str.replace_all(p, s))


# Result of error in export script, newlines were replaced with '',
# causing some phrases to run into each other when not punctuated.
# WARNING: Do not use on German lang.
def clean_text_missing_newline(df, column="problem"):

    pattern = r"(([A-z]+[a-z]{1})([A-Z][A-z]+))"
    exclude = [
        "youtube",
        "chatgpt",
        "macos",
        "chromeflex",
        "chromeos",
        "winos",
        "winxp",
        "winpe",
        "wifi",
        "hifi",
        "cloudready",
        "whatsapp",
        "bluetooth",
        "nimh",
        "winrar",
        "exfat",
        "nicd",
        "microusb",
        "openwrt",
        "lipo",
        "microfahrad",
        "onedrive",
        "treesize",
        "mcafee",
        "repaircafe",
        "repaircafé",
        "tomtom",
        "nicad",
    ]

    def fix_text(text):
        matches = re.search(pattern, text, re.MULTILINE)
        if matches != None:
            if not matches.group(0).lower in exclude:
                text = re.sub(pattern, "\\2. \\3", text, re.MULTILINE)
        return text

    df = df.with_columns(
        pl.col(column)
        .map_elements(lambda s: fix_text(s), return_dtype=pl.String)
        .alias(column)
    )

    return df
