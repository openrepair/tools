# APACHE SOLR TEST DATA

For use with Solr cores nested under the "test" folder.

## test_lang.csv

Set of real and fake `group_identifier` strings for testing international characters and phonetic matching.

### Filter accents

#### Groups with any variation of the word "cafe", i.e. "Café", "café", "Cafe"

Not phonetic, exact spelling, case-insensitive.

Query with a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:cafe`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":0,
    "params":{
      "q":"text_general:cafe",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":7,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Cafe Belfast"},
      {
        "text_general":"Repair Cafe Blefast"},
      {
        "text_general":"Repair Cafe Malmö"},
      {
        "text_general":"Repair Cafe Malmo"},
      {
        "text_general":"Repair Cafe Blenny"},
      {
        "text_general":"Repair cafe Portsmouth"},
      {
        "text_general":"Repair Cafe de Neufchateau"}]
}}
```

Query with an [ICU](https://unicode-org.github.io/icu/userguide/icu4j/why-use-icu4j.html) field type

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_icuFolding:cafe`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":0,
    "params":{
      "q":"text_icuFolding:cafe",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":12,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Café Danmark"},
      {
        "text_general":"Repair Café Denmark"},
      {
        "text_general":"Repair Café Portsmouth"},
      {
        "text_general":"Repair Cafe Belfast"},
      {
        "text_general":"Repair Cafe Blefast"},
      {
        "text_general":"Repair Cafe Malmö"},
      {
        "text_general":"Repair Café Blégny"},
      {
        "text_general":"Repair Cafe Malmo"},
      {
        "text_general":"Repair Cafe Blenny"},
      {
        "text_general":"Repair cafe Portsmouth"},
      {
        "text_general":"Repair Café de Neufchâteau"},
      {
        "text_general":"Repair Cafe de Neufchateau"}]
}}
```

#### Look for a repair cafe in "Malmö"

Not phonetic, exact spelling, case-insensitive.

Query with a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:malmo`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_general:malmo",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":1,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Cafe Malmo"}]
}}
```

Query with an [ICU](https://unicode-org.github.io/icu/userguide/icu4j/why-use-icu4j.html) field type

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_icuFolding:malmo`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_icuFolding:malmo",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":2,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Cafe Malmö"},
      {
        "text_general":"Repair Cafe Malmo"}]
}}
```

## Sorting strings with international characters

With no sort order.

`http://localhost:8983/solr/test_lang/select?indent=true&fl=text_general&q=text_general:*&rows=18`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":0,
    "params":{
      "q":"text_general:*",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":18,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Café Danmark"},
      {
        "text_general":"Repair Café Denmark"},
      {
        "text_general":"Repair Café Portsmouth"},
      {
        "text_general":"Repair Cafe Belfast"},
      {
        "text_general":"Repair Cafe Blefast"},
      {
        "text_general":"Repair Cafe Malmö"},
      {
        "text_general":"Repair Café Blégny"},
      {
        "text_general":"Ōtautahi Repair Revolution"},
      {
        "text_general":"Otautahi Repair Revolution"},
      {
        "text_general":"LES 100TINEL Fix Club Bénin"},
      {
        "text_general":"LES 100TINEL Fix Club Benin"},
      {
        "text_general":"Repair Café de Neufchâteau"},
      {
        "text_general":"Repair Cafe de Neufchateau"},
      {
        "text_general":"Repair Cafe Malmo"},
      {
        "text_general":"Repair Cafe Blenny"},
      {
        "text_general":"Repair Caf Foo"},
      {
        "text_general":"Repair caff Bar"},
      {
        "text_general":"Repair cafe Portsmouth"}]
}}
```

Sorted on a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&fl=text_general&q=text_general:*&rows=18&sort=text_general asc`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_general:*",
      "indent":"true",
      "fl":"text_general",
      "sort":"text_general asc",
      "rows":"18"}},
  "response":{"numFound":18,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"LES 100TINEL Fix Club Bénin"},
      {
        "text_general":"LES 100TINEL Fix Club Benin"},
      {
        "text_general":"Repair caff Bar"},
      {
        "text_general":"Repair Cafe Belfast"},
      {
        "text_general":"Repair Cafe Blefast"},
      {
        "text_general":"Repair Cafe Blenny"},
      {
        "text_general":"Repair Café Blégny"},
      {
        "text_general":"Repair Caf Foo"},
      {
        "text_general":"Repair Cafe Malmö"},
      {
        "text_general":"Repair Cafe de Neufchateau"},
      {
        "text_general":"Repair Cafe Malmo"},
      {
        "text_general":"Repair cafe Portsmouth"},
      {
        "text_general":"Repair Café Danmark"},
      {
        "text_general":"Repair Café Denmark"},
      {
        "text_general":"Repair Café Portsmouth"},
      {
        "text_general":"Repair Café de Neufchâteau"},
      {
        "text_general":"Otautahi Repair Revolution"},
      {
        "text_general":"Ōtautahi Repair Revolution"}]
}}
```

Sorted on an [ICU collation](https://solr.apache.org/docs/9_0_0/modules/analysis-extras/org/apache/solr/schema/ICUCollationField.html) field type.

`http://localhost:8983/solr/test_lang/select?indent=true&fl=text_general&q=text_general:*&rows=18&sort=collatedROOT asc`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":0,
    "params":{
      "q":"text_general:*",
      "indent":"true",
      "fl":"text_general",
      "sort":"collatedROOT asc",
      "rows":"18"}},
  "response":{"numFound":18,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"LES 100TINEL Fix Club Bénin"},
      {
        "text_general":"LES 100TINEL Fix Club Benin"},
      {
        "text_general":"Ōtautahi Repair Revolution"},
      {
        "text_general":"Otautahi Repair Revolution"},
      {
        "text_general":"Repair Caf Foo"},
      {
        "text_general":"Repair Cafe Belfast"},
      {
        "text_general":"Repair Cafe Blefast"},
      {
        "text_general":"Repair Café Blégny"},
      {
        "text_general":"Repair Cafe Blenny"},
      {
        "text_general":"Repair Café Danmark"},
      {
        "text_general":"Repair Café de Neufchâteau"},
      {
        "text_general":"Repair Cafe de Neufchateau"},
      {
        "text_general":"Repair Café Denmark"},
      {
        "text_general":"Repair Cafe Malmö"},
      {
        "text_general":"Repair Cafe Malmo"},
      {
        "text_general":"Repair Café Portsmouth"},
      {
        "text_general":"Repair cafe Portsmouth"},
      {
        "text_general":"Repair caff Bar"}]
}}
```

### Phonetic matching

Look for groups in Denmark, which can be listed as Danmark.

#### Query with a vanilla `text_general` field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:denmark`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_general:denmark",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":1,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Café Denmark"}]
}}
```

#### Query with a Double Metaphone field

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_doubleMetaphone:denmark`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_doubleMetaphone:denmark",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":2,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Repair Café Danmark"},
      {
        "text_general":"Repair Café Denmark"}]
}}
```

#### Query with a Beider Morse field

To Do: not working properly?

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_BeiderMorse:denmark`

### Combined accent filter and phonetic match

Look for group "Ōtautahi Repair Revolution" using a miss-spelling that involves both a wrong character and wrong character order.

Query with a vanilla `text_general field.

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_general:Otuatahi`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_general:Otuatahi",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":0,"start":0,"numFoundExact":true,"docs":[]
}}
```

Query with a field indexed using both Double Metaphone phonetic algorithm and an [ICU](https://unicode-org.github.io/icu/userguide/icu4j/why-use-icu4j.html) filter

`http://localhost:8983/solr/test_lang/select?indent=true&rows=18&fl=text_general&q=text_icufdm:Otuatahi`

```json
{
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"text_icufdm:Otuatahi",
      "indent":"true",
      "fl":"text_general",
      "rows":"18"}},
  "response":{"numFound":2,"start":0,"numFoundExact":true,"docs":[
      {
        "text_general":"Ōtautahi Repair Revolution"},
      {
        "text_general":"Otautahi Repair Revolution"}]
}}
```

## Links

[The Missing Guide to the ICU Message Format](https://phrase.com/blog/posts/guide-to-the-icu-message-format/)
[Class ICUCollationField](https://solr.apache.org/docs/9_0_0/modules/analysis-extras/org/apache/solr/schema/ICUCollationField.html)
[Phonetic Matching](https://solr.apache.org/guide/solr/9_1/indexing-guide/phonetic-matching.html)
[Phonetic Matching with Apache Solr - Slideshare](https://www.slideshare.net/MarkusGnther9/phonetic-matching-with-apache-solr)
[Understanding phonetic matching](https://subscription.packtpub.com/book/data/9781788837385/4/ch04lvl1sec33/understanding-phonetic-matching)
