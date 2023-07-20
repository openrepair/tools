# APACHE SOLR TEST DATA

For use with Solr cores nested under the "test" folder.

## test_lang.csv

Set of real and fake `group_identifier` strings for testing international characters and phonetic matching.

### Filter accents

#### Groups with any variation of the word "cafe", i.e. "Café", "café", "Cafe"

Not phonetic, exact spelling, case-insensitive.

Query with a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:cafe`

![Results](img/cafe-text_general.png "Results")

Query with an [ICU](https://unicode-org.github.io/icu/userguide/icu4j/why-use-icu4j.html) field type

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_icuFolding:cafe`

![Results](img/cafe-text_icuFolding.png "Results")

#### Look for a repair cafe in "Malmö"

Not phonetic, exact spelling, case-insensitive.

Query with a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:malmo`

![Results](img/malmo-text_general.png "Results")

Query with an [ICU](https://unicode-org.github.io/icu/userguide/icu4j/why-use-icu4j.html) field type

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_icuFolding:malmo`

![Results](img/malmo-text_icuFolding.png "Results")

## Sorting strings with international characters

With no sort order.

`http://localhost:8983/solr/test_lang/select?indent=true&fl=text_general&q=text_general:*&rows=18`

![Results](img/sorting-none.png "Results")

Sorted on a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&fl=text_general&q=text_general:*&rows=18&sort=text_general asc`

![Results](img/sorting-text_general.png "Results")

Sorted on an [ICU collation](https://solr.apache.org/docs/9_0_0/modules/analysis-extras/org/apache/solr/schema/ICUCollationField.html) field type.

`http://localhost:8983/solr/test_lang/select?indent=true&fl=text_general&q=text_general:*&rows=18&sort=collatedROOT asc`

![Results](img/sorting-text_icucollation.png "Results")

### Phonetic matching

Look for groups in Denmark, which can be listed as Danmark.

#### Query with a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:denmark`

![Results](img/denmark-text_general.png "Results")

#### Query with a Double Metaphone field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_doubleMetaphone:denmark`

![Results](img/denmark-text_doublemetaphone.png "Results")

#### Query with a Beider Morse field

To Do: not working properly?

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_BeiderMorse:denmark`

### Combined accent filter and phonetic match

Look for group "Ōtautahi Repair Revolution" using a miss-spelling that involves both a wrong character and wrong character order.

Query with a vanilla `text_general field.

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:Otuatahi`

![Results](img/otuatahi-text_general.png "Results")

Query with a field indexed using both Double Metaphone phonetic algorithm and an [ICU](https://unicode-org.github.io/icu/userguide/icu4j/why-use-icu4j.html) filter

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_icufdm:Otuatahi`

![Results](img/otuatahi-text_icufdm.png "Results")

## Links

[The Missing Guide to the ICU Message Format](https://phrase.com/blog/posts/guide-to-the-icu-message-format/)
[Class ICUCollationField](https://solr.apache.org/docs/9_0_0/modules/analysis-extras/org/apache/solr/schema/ICUCollationField.html)
[Phonetic Matching](https://solr.apache.org/guide/solr/9_1/indexing-guide/phonetic-matching.html)
[Phonetic Matching with Apache Solr - Slideshare](https://www.slideshare.net/MarkusGnther9/phonetic-matching-with-apache-solr)
[Understanding phonetic matching](https://subscription.packtpub.com/book/data/9781788837385/4/ch04lvl1sec33/understanding-phonetic-matching)
