# About Open Repair Tools

```
We had a kettle; we let it leak:
Our not repairing made it worse.
We haven`t had any tea for a week...
The bottom is out of the Universe.
― Rudyard Kipling
```

Not so much a project as a mixed bag of tools, queries, data and code snippets for use with Open Repair Data (ORDS).

For anyone who fancies tinkering with Python, NLP, SQL and lots of messy but interesting Open Data. Many challenges lie ahead!

Some of the things you can do:

* Get familiar with ORDS data.
* Slice the data up in various ways using Python DataFrames and/or MySQL/SQLite.
* Investigate devices against the timeline of consumer electronics.
* Calculate how much waste was prevented from going to landfill.
* Detect languages in the text and translate using the DeepL API.
* Muck about with regular expressions.
* Try out some Natural Language Processing and even a little basic machine learning.
* Generate [Open Repair Poetry](./poetry).

There is also an [installer and ORDS configuration](solr/README.md) for an Apache Solr search platform that demonstrates indexing and querying multi-lingual text with international (ICU) characters.

## About the data

The dataset contains over 100k records representing over 10 years worth of electronic repairs at events by community repair groups all over the world. See the Setup section below for how to get hold of the data.

It is compiled and published by the [Open Repair Alliance (ORA)](https://openrepair.org/) an organisation founded by [The Restart Project](https://therestartproject.org/), a UK based charity.

* Enabling thousands of UK-based community repair events.
* Formulating the [Open Repair Data Standard](https://openrepair.org/open-data/open-standard/).
* Compiling and publishing the ORDS data twice yearly.
* Organisers of [FixFest](https://fixfest.therestartproject.org/), a regular global gathering of repairers and tinkerers, activists, policy-makers, thinkers, educators and companies from all over the world.
* Winners of the [European Union Prize for Citizen Science Digital Communities Award](https://ars.electronica.art/citizenscience/en/the-restart-project-the-right-to-repair-and-reuse-your-electronics/) for demonstrating excellence in creating and supporting communities, delivering social benefits, and fostering an open and inclusive civil society through the innovative or alternative use of digital technologies.

## Lots of things yet to do

* Use-cases
* Tests
* Data visualisation
* Document all the things
* Clean up poor quality code
* Sort out requirements
* Refactor pandas to polars for speed and clarity

## Licences & acknowledgments

* Code
  * [GNU General Public License v3.0](LICENSE.txt)
* [Data](dat/README.md)
  * [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (Creative Commons Attribution-ShareAlike 4.0 International)
* [ORDS Quest Data](https://github.com/openrepair/data) is covered by the license for [ORDS Data](https://openrepair.org/open-data/downloads/)
  * [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (Creative Commons Attribution-ShareAlike 4.0 International)

## Setup

### Requirements

* Python with venv module.
* Optional MySQL 8.x and libmysqlclient-dev.

### Virtual environment

```python3 -m venv ords-tools```

```cd ords-tools```

```git init```

```git remote add origin git@github.com:openrepair/tools.git```

```git pull origin main```

```git branch --set-upstream-to=origin/main main```

```source bin/activate```

```pip install -r requirements.txt```

### Data

Grab the [Aggregated Open Repair Data files](https://openrepair.org/open-data/downloads/), unzip the files into the [dat/ords](./dat/ords) directory.

### Environment variables

Copy ```.env.example``` to ```.env``` and edit as necessary.

```.env``` is in .gitignore, do not add it to this repo.

## Links

### Repair data

[Open Repair on Github](https://github.com/openrepair/data/tree/master)

[ORDS data downloads](https://openrepair.org/open-data/downloads/)

[Open Repair Alliance](https://openrepair.org/)

### Python

[Python](https://docs.python.org/)

[Scikit-learn](https://scikit-learn.org/)

[Natural Language Processing Demystified](https://www.nlpdemystified.org/)

[Pythex](https://pythex.org/)

### Other tools

[MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)

[Solr](https://solr.apache.org/)
