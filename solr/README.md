# APACHE SOLR

Install an [Apache Solr 9.2.1 search platform](https://solr.apache.org/) for use with ORDS data.

The result will be a very basic, out-of-the-box installation for local use without any security hardening and therefore not suitable for deployment.

## Requirements

1. Linux Bash terminal
2. Java >= 17
3. cURL
4. wget
5. Local web server
6. Web browser
7. ORDS data csv file in the `ords-tools/dat/ords` folder

## Set up

`bash install.sh`

The install script will

1. Check for Solr package and download if not found.
2. Extract contents.
3. Copy the ORDS and test core configuration files to the Solr home directory.
4. Start Solr and load the cores.
5. Import the test data to the test core.
6. Import the ORDS data to the ORDS core.

## After installation

In a web browser, navigate to `http://localhost:8983/solr` and you should see the Solr dashboard.

If there is no "Core Selector" box, wait a few seconds and refresh page.

## Commands

### Start Solr

#### Linux

`solr-9.2.1/bin/solr start`

#### Windows Subsytem Linux (WSL)

`solr-9.2.1/bin/solr start -Dsolr.jetty.host="0.0.0.0"`

### Stop Solr

`solr-9.2.1/bin/solr stop`

## Usage

### Standard Query Parser

Out of the box, Solr's Standard Query Parser provides a wide variety of search handling functionality.

[Boolean Operators](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#boolean-operators-supported-by-the-standard-query-parser)
[Wildcard Searches](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#wildcard-searches)
[Fuzzy matching](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#fuzzy-searches)
[Proximity Searches](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#proximity-searches)
[Range Searches](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#range-searches)
[Boosting](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#boosting-a-term-with)
[Sub-Queries](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#grouping-terms-to-form-sub-queries)

### Other parsers and complex handlers are available

[Query Syntax and Parsers](https://solr.apache.org/guide/solr/latest/query-guide/query-syntax-and-parsers.html)

### Customised parsing

The `test_lang` core demonstrates more custom functionality to handle international characters and phonetic matching.

See [core/data/README.md](core/data/README.md) for details of the test_lang core and example queries.

### Other useful functionality

[Spell Checking](https://solr.apache.org/guide/solr/latest/query-guide/spell-checking.html)
[Faceting](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html)
[Suggester](https://solr.apache.org/guide/solr/latest/query-guide/suggester.html)
[MoreLikeThis](https://solr.apache.org/guide/solr/latest/query-guide/morelikethis.html)

## To Do

1. Tidy up config and schema files
2. Implement spellchecking and synonyms
3. [Language detection](https://solr.apache.org/guide/solr/latest/indexing-guide/language-detection.html)
4. [OpenNLP integration](https://solr.apache.org/guide/solr/latest/indexing-guide/language-analysis.html#opennlp-integration)

## Links

[System requirements](https://solr.apache.org/guide/solr/latest/deployment-guide/system-requirements.html)
[Installation](https://solr.apache.org/guide/solr/latest/deployment-guide/installing-solr.html)
[Github](https://github.com/apache/solr)
[Java versions](https://endoflife.date/java)