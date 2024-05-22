import re


def clean_text(df, column="problem", dropna=True, strip=True, dedupe=True):

    clean_text_sentences(df, column)

    clean_text_html_tags(df, column)

    clean_text_html_symbols(df, column)

    clean_text_weights(df, column)

    clean_text_code_prefixes(df, column)

    clean_text_nonprinting_chars(df, column)

    clean_text_missing_newline(df, column)

    if strip:
        # Trim whitespace.
        df[column] = df[column].str.strip()

    if dropna:
        # Drop column values that may be empty after the replacements and trimming.
        df[column].replace("", None, inplace=True)
        df.dropna(subset=[column], inplace=True)

    if dedupe:
        # Dedupe the column values.
        df.drop_duplicates(subset=[column], inplace=True)
        print(df.index.size)

    return df


# Make sure there is always a space after a period, else sentences won't be split.
def clean_text_sentences(df, column="problem"):

    df.replace(
        {column: r"(?i)(([a-zß-ÿœ])\.([a-zß-ÿœ]))"},
        {column: "\\2. \\3"},
        regex=True,
        inplace=True,
    )
    return df


# Remove HTML symbols (&gt; features a lot)
def clean_text_html_symbols(df, column="problem"):

    df.replace({column: r"(?i)(&[\w\s]+;)"}, {column: ""}, regex=True, inplace=True)
    return df


# Remove HTML tags
def clean_text_html_tags(df, column="problem"):

    df.replace(
        {column: r"(?i)<\/?[a-z][a-z0-9]*[^<>]*>|<!--.*?-->"},
        {column: ""},
        regex=True,
        inplace=True,
    )
    return df


# Remove weight values (0.5kg, 5kg, 5 kg, .5kg etc.)
def clean_text_weights(df, column="problem"):

    df.replace(
        {column: r"(?i)(([0-9]+)?\.?[0-9\s]+kg)"},
        {column: ""},
        regex=True,
        inplace=True,
    )
    return df


# Remove random non-alpha codes often found prefixing `problem` strings.
def clean_text_code_prefixes(df, column="problem"):

    df.replace(
        {column: r"(?i)^(\W|\d+)([\d|\W]+)?"},
        {column: ""},
        regex=True,
        inplace=True,
    )
    return df


# Some literal eol chars are embedded.
def clean_text_nonprinting_chars(df, column="problem"):

    df.replace(
        {column: r"(\\+(r|n))"},
        {column: " "},
        regex=True,
        inplace=True,
    )
    return df


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

    df[column] = df[column].apply(lambda s: fix_text(s))

    return df
