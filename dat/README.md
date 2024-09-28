# Data

To use these scripts you will need the aggregated Open Repair Data as well as the data in the `dat` directory

## Open Repair Data

A dataset comprising records that conform to the [Open Repair Data Standard](https://openrepair.org/open-data/open-standard/).

Download the core data from the [Open Repair Alliance (ORA)](https://openrepair.org/open-data/downloads/) and unzip the files into the [dat/ords](./ords) directory.

The data is recorded by volunteers and participants at community repair events, it is collected by networks of organisers who are [members and allies](https://openrepair.org/members/) of the the [Open Repair Alliance](https://openrepair.org/). It comes from hundreds of community groups in over two dozen countries with multiple languages represented.

Once or twice a year [The Restart Project](https://therestartproject.org/) gathers the contributed data and transforms it to comply with the Open Repair Standard. The results are published as Open Data, freely available for download by anyone. The data and the standard are held in a public [Git repository](https://github.com/openrepair).

To get an idea of the effort and challenges involved in recording repair data at live community events, take a look at [Repair data collection tips and tools](https://docs.google.com/document/d/1s9MHVIdx2jMeMq0x3qGd80suHVdupLvYYOWaAi1jq3A/edit?usp=sharing)

Some of the resources available to community repairers and data collectors:

* [Community](https://talk.restarters.net/)
* [Insights & stories](https://openrepair.org/open-data/insights/)
* [Guides](https://wiki.restarters.net/Main_Page)
* [Campaigns](https://repair.eu/)

> Each item in our database represents a citizen who took hours out of their life to learn what went wrong with their device, and to learn how to fix it. This makes our data more powerful than any petition or online complaint.

## Files in the data quests directory

See the [Quests README](./quests/README.md)

## Files in the data directory

These files contain data used by the scripts in this repository.

### `consumer_electronics_timeline.csv`

Timeline of electronic inventions and commercial availability related to ORDS product categories.

### `iso_country_codes.csv`

List of 3 character codes and country short-names.

### `ords_lang_training_stopwords.txt`

List of common abbreviations to filter out when training the repair language model.

### `ords_problem_translations.csv`

Work-in-progress to translate the entire ORDS dataset into each of English, Dutch, German, French, Spanish, Danish and Italian.

### `ords_product_category_item_type_translations.csv`

List of some of the device types per `product_category`. Translations in English, Dutch, German, French.

### `ords_product_category_unu_key_map.csv`

Maps the ORDS `product_category` values to a set known as "UNU Keys" produced by [UNITAR - United Nations Institute for Training and Research](https://www.unitar.org/). These keys are commonly found in academic papers dealing with  subjects around e-waste and trickle out to wider reports and news stories, e.g. [OF 16 BILLION MOBILE PHONES POSSESSED WORLDWIDE, 5.3 BILLION WILL BECOME WASTE IN 2022](https://www.unitar.org/about/news-stories/news/16-billion-mobile-phones-possessed-worldwide-53-billion-will-become-waste-2022). Note that UNITAR is reviewing their codes as part of a 4 year project due to conclude December 2023.

The UNU average weights (kgs) in the file are lifted from [E-waste statistics: Guidelines on classifications, reporting and indicators](https://www.researchgate.net/publication/271845217_E-waste_statistics_Guidelines_on_classifications_reporting_and_indicators).

Not all ORDS categories can be directly mapped to other sets of product categories. Combining category maps with queries to find item types could produce better results.

The Restart Project compiles emissions and waste data that can be mapped to ORDS and UNU categories, for details [contact them directly](https://therestartproject.org/contact/).

### `ords_testdata_common_products.csv`

A list of common item types found in the ORDS data. Mostly English.

### `ords_testdata_multilingual_products.csv`

A list of common item types found in the ORDS data. English, Dutch, French and German with a little Italian and Spanish.

### `product_category_regex_elements.csv`

Lists of terms and regex snippets used by ords_regex_category_compiler.py. English, Dutch, French and German with a little Italian and Spanish.

### `product_category_regexes.csv`

A set of Regular Expressions used by ords_regex_category_tester.py and compiled by ords_regex_category_compiler.py.

### `stopwords-english-repair.txt`

List of repair-related stopwords extracted from the ORDS corpus using `ords_extract_vocabulary.py`.

### `stopwords-english.txt`

List of English stopwords from a dataset published on [Kaggle](https://www.kaggle.com/datasets/rtatman/stopword-lists-for-19-languages). "This dataset is Copyright (c) 2005, Jacques Savoy and distributed under the [BSD License](https://opensource.org/license/bsd-2-clause/)."

### `tableschema_ords_mysql.sql`

An SQL script for creating a MySQL table to hold the ORDS data. It is used by ords_database_setup.py and requires the name of the ORDS filename to be set in the .env file.

### `tableschema_translations_mysql.sql`

An SQL script for creating a MySQL table to hold the ORDS translations.
