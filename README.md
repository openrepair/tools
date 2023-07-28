# About this project

```
We had a kettle; we let it leak:
Our not repairing made it worse.
We haven`t had any tea for a week...
The bottom is out of the Universe.
― Rudyard Kipling
```

Not so much a project as a mixed bag of tools, queries, data and code snippets for use with Open Repair Data (ORDS).

For anyone who fancies tinkering with Python, SQL, NLP and lots of messy but interesting Open Data. Many challenges lie ahead!

Some of the things you can do:

* Get familiar with ORDS data.
* Set up a MySQL database for ORDS data.
* Slice the data up in various ways.
* Investigate devices against the timeline of consumer electronics.
* Calculate how much waste was prevented from going to landfill.
* Detect languages in the text and translate using the DeepL API.
* Muck about with regular expressions.
* Try out some Natural Language Processing and even a little (very basic) machine learning.
* Generate Open Repair Data poetry.

There is also an [installer and ORDS configuration](solr/README.md) for an Apache Solr search platform that demonstrates indexing and querying multi-lingual text with international (ICU) characters.

## About the data

The dataset contains over 100k records representing over 10 years worth of electronic repairs at events by community repair groups all over the world. See the Setup section for how to get hold of the data.

It is compiled and published by the [Open Repair Alliance](https://openrepair.org/) (ORA) which was founded by [The Restart Project](https://therestartproject.org/), a UK based charity.

* Enabling thousands of UK-based community repair events.
* Formulating the [Open Repair Data Standard](https://openrepair.org/open-data/open-standard/).
* Compiling and publishing the ORDS data twice yearly.
* Organisers of [FixFest](https://fixfest.therestartproject.org/), a regular global gathering of repairers and tinkerers, activists, policy-makers, thinkers, educators and companies from all over the world.
* Winners of the [European Union Prize for Citizen Science Digital Communities Award](https://ars.electronica.art/citizenscience/en/the-restart-project-the-right-to-repair-and-reuse-your-electronics/) for demonstrating excellence in creating and supporting communities, delivering social benefits, and fostering an open and inclusive civil society through the innovative or alternative use of digital technologies.

## Lots of things yet to do

* Investigate use-cases.
* Write a few tests.
* Data visualisation.
* Document all the things.

## Licences & acknowledgments

* Code
  * [GNU General Public License v3.0](LICENSE.txt)
* [Data](dat/README.md)
  * [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (Creative Commons Attribution-ShareAlike 4.0 International)
* [ORDS Quest Data](https://github.com/openrepair/data) is covered by the license for [ORDS Data](https://openrepair.org/open-data/downloads/)
  * [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (Creative Commons Attribution-ShareAlike 4.0 International)

## Setup

### Requirements

* Venv module.
* Database is used in some scripts, will need libmysqlclient-dev
* MySQL version 8.x assumed but other MySQL versions should work with installation of compatible connector.

### Working copy

```git clone git@github.com:openrepair/tools.git ./ords-tools```

### Virtual environment

```python3 -m venv ords-tools```

```cd ords-tools```

```source bin/activate```

To install the requirements.

```pip install -r requirements.txt```

To upgrade to the newest requirements.

```pip install -r requirements.txt --upgrade```

### Data

Grab the [Aggregated Open Repair Data files](https://openrepair.org/open-data/downloads/), unzip the files into the [data](./dat) directory.

### Environment variables

Copy ```.env.example``` to ```.env``` and edit as necessary.

```.env``` is in .gitignore, do not add it to this repo.

[.env file documentation](https://saurabh-kumar.com/python-dotenv/#file-format)

## Links

### Repair data

[Open Repair on Github](https://github.com/openrepair/data/tree/master)

[ORDS data downloads](https://openrepair.org/open-data/downloads/)

[Open Repair Alliance](https://openrepair.org/)

### Python

[Python and Virtual Environments](https://csguide.cs.princeton.edu/software/virtualenv#scm)

[Using Python environments in VS Code](https://code.visualstudio.com/docs/python/environments)

[Python](https://docs.python.org/)

[W3 Schools Python](https://www.w3schools.com/python/)

[Numpy](https://numpy.org/)

[Pandas](https://pandas.pydata.org/)

[Scikit-learn](https://scikit-learn.org/)

[Natural Language Processing Demystified](https://www.nlpdemystified.org/)

[Pythex](https://pythex.org/)

### Other tools

[MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)

[OpenRefine](https://openrefine.org/)

[R](https://www.r-project.org/)

[Apache OpenNLP](https://opennlp.apache.org/)

[Solr](https://solr.apache.org/)

[Data-Driven Documents (D3)](https://d3js.org/)

[Orange](https://orangedatamining.com/)
