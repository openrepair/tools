# What

## Open Repair Data

A dataset comprising records that conform to the [Open Repair Data Standard](https://openrepair.org/open-data/open-standard/).

### Who

The data is recorded by volunteers and participants at community repair events.

The data is contributed by [members and allies](https://openrepair.org/members/) of the the [Open Repair Alliance](https://openrepair.org/) (ORA).

It is compiled and published by [The Restart Project](https://therestartproject.org/).

### When

Twice a year The Restart Project collects the data from the ORA partners, converting it to use the standard and publishing the results as Open Data, freely available for download by anyone. The data and the standard are also published in a [Git repository](https://github.com/openrepair).

### Where

It comes from all over the world, over two dozen countries and multiple languages represented.

### How

[How to record repairs](https://openrepair.org/how-to-get-started/)

To get an idea of the effort and challenges involved in recording repair data at live community events, take a look at [Repair data collection tips and tools](https://docs.google.com/document/d/1s9MHVIdx2jMeMq0x3qGd80suHVdupLvYYOWaAi1jq3A/edit?usp=sharing)

### Why

* [Community](https://talk.restarters.net/)
* [Insights & stories](https://openrepair.org/open-data/insights/)
* [Guides](https://wiki.restarters.net/Main_Page)
* [Campaigns](https://repair.eu/)

> Each item in our database represents a citizen who took hours out of their life to learn what went wrong with their device, and to learn how to fix it. This makes our data more powerful than any petition or online complaint.

## Other files in the dat directory

### tableschema_ords_mysql.sql

An SQL script for creating a MySQL table to hold the ORDS data. It is used by ords_database_setup.py and requires the name of the ORDS filename to be set in the .env file.

### product_category_regexes.csv

A set of Regular Expressions used by ords_regex_category_tester.py and compiled by ords_regex_category_compiler.py.

### product_category_regex_elements.csv

Lists of terms and regex snippets used by ords_regex_category_compiler.py. English, Dutch, French and German with perhaps a little Italian and Spanish.

### consumer_electronics_timeline.csv

Timeline of electronic inventions and commercial availability related to ORDS product categories.

### ords_category_lca_reference.csv

Average weights and carbon footprints relating to ORDS product categories. Based on lifecycle assessment work carried out by The Restart Project.
[The environmental impact of our devices: revealing what many companies hide](https://therestartproject.org/consumption/hidden-impact-devices/)

### ords_testdata_common_products.csv

A list of common item types found in the ORDS data. Mostly English.

### ords_testdata_multilingual_products.csv

A list of common item types found in the ORDS data. English, Dutch, French and German with perhaps a little Italian and Spanish.

### ords_problem_translations.csv

Work-in-progress to translate the entire ORDS dataset into each of English, Dutch, German, French, Spanish and Italian. Other languages will be implemented in time.

### tableschema_translations_mysql.sql

An SQL script for creating a MySQL table to hold the ORDS translations. Required by the ords_deepl* scripts.

### iso_country_codes.csv

List of 3 character codes and country short-names.

### stopwords-english.txt

List of English stopwords from a dataset published on [Kaggle](https://www.kaggle.com/datasets/rtatman/stopword-lists-for-19-languages). "This dataset is Copyright (c) 2005, Jacques Savoy and distributed under the [BSD License](https://opensource.org/license/bsd-2-clause/)."

### stopwords-english-repair.txt

List of repair-related stopwords extracted from the ORDS corpus using `ords_extract_vocabulary.py`.

### ords_product_category_item_type_translations.csv

List of device type names per `product_category`. Translations in English, Dutch, German, French.
