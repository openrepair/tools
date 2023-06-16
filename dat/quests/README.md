# Quests

Data is collected at community events and enriched via quests to become strong evidence for better products. With the help of data volunteers we can change the system.

Quests are forays into Open Repair Data organised by [The Restart Project](https://restarters.net/workbench) with volunteers from the repair community using datasets published by the [Open Repair Alliance](https://openrepair.org/)

A Quest is an activity that digs into the repair data to uncover insights. It takes the form of a "microtask" involving a group of humans who are presented with data for consideration and then asked to form an opinion and choose an answer from a list of options. Typically our Quests involve repair data selected for a selected category, a curated list of common fault type options for that category, and the humans are usually asked to decide what is the likely type of fault present in each record.

## A brief history of Quests

The first one was held in person on a Saturday afternoon in March 2019 for Open Data Day. A group of over a dozen members of the community gathered at Newspeak House, in London’s Shoreditch to look at records of repair attempts on laptops, desktops and tablets. Data from the Restart Project’s [Fixometer](https://therestartproject.org/fixometer-2/) was simply presented in spreadsheets.

A second in-person workshop was held as part of [FixFest 2019](https://reparatur-festival.runder-tisch-reparatur.de/fixfest-2019/) at Mozilla Repair data dive in Berlin. This time we were joined by one of the Open Repair Alliance partners, anstiftung and again we looked at laptops, desktops and tablets using data from both The Restart Project and anstiftung.

These early experiments were a great success, we learned a lot, had fun and were able to produce some really useful results. It was decided to try and extend the reach and the engagement of the community by turning the live events into online “apps”. This turned out to be a timely decision given the onset of the Covid pandemic a few months later.

## A timeline of our Quests to date

| Title      | Date     | Device types               | Data source     | Notes             |
|------------|----------|----------------------------|-----------------|-------------------|
| FaultCat   | Dec 2019 | Laptops, desktops, tablets | Restart Project | “CompCat”         |
| MiscCat    | Mar 2020 | All electrical devices     | Restart Project | Not “fault types” |
| MobiFix    | Jul 2020 | Mobile phones              | Restart Project |                   |
| MobiFixOra | Mar 2021 | Mobile phones              | ORA partners    |                   |
| TabiCat    | Jun 2021 | Tablets                    | ORA partners    | ACTION quest      |
| PrintCat   | Apr 2021 | Printers                   | ORA partners    | ACTION quest      |
| BattCat    | Jul 2021 | Battery-powered devices    | ORA partners    | ACTION quest      |
| DustUp     | Jun 2022 | Vacuum cleaners            | ORA partners    |                   |

## How we build a Quest

As well as hosting UK-based community repair events, [The Restart Project](https://therestartproject.org/) founded the [Open Repair Alliance](https://openrepair.org/) and formulated the [Open Repair Data Standard](https://openrepair.org/open-data/open-standard/). Twice a year we  undertake the task of collecting data from the ORA partners around the world, converting it to use the standard and publishing the resulting datasets as Open Data, freely available as public downloads. Both the data and the standard are also published in a [Git repository](https://github.com/openrepair).

Initially, data we used in Quests came from the Restart Project’s Fixometer. Since then we’ve expanded our horizons and mostly use ORA data.

Several steps are required to prepare the data for use in a Quest.

* Extract the domain data from the latest ORA dataset. We sift out the data classified for the domain, e.g. “vacuum cleaner”. Sometimes, if there is no straightforward classification we have to search the “problem” text for words that match our domain, e.g. a quest called BattCat was about any battery-powered device so we had to search for mentions of batteries.
* Evaluate the quality of the extracted data given the domain goal. Usually the goal is to put records into buckets of “fault types”, therefore we will need records that have enough information to yield the source of the fault for that device.
* Exclude records that have no useful “problem” text. The data comes from community repair events staffed by volunteers, and often it is entered into databases some time after the event. It is far from perfect, sometimes there is nothing or very little description of the problem or solution provided. The very first quests did not exclude poor data and participants had to label a lot of records with fault type "Unknown", later this option was renamed "Poor data".
* Translate the “problem” text. ORA data arrives in a variety of languages and the Quest participants are often situated in many different countries. In order to be as inclusive as possible we want each record’s “problem” text available in each of the six languages that we are able to cater for. We learned over time to match participants with records of their own language as a priority. When own-language record ran out for a participant they would be offered other language records either pre-translated for them or with the an easy to reach translation tool such as Google Translate or DeepL.
* Compile a list of potential “fault types”. This is done by parsing and querying the (English and English-translated) “problem” text to assess and quantify the terminology used. For example with vacuum cleaners, words such as “suction”, “suck”, “brush”,  “wheel”, “motor”, “battery” etc. appeared frequently. Some of our policy partners also provided their own lists of “fault types”. Combining these two sources we create the list of “fault types” that we used in a Quest.
* Compile a list of “suggestions”. The list of common terms that were deduced in the previous step is then used to check each record as it is presented to the user and to pull up a list of possible “fault types”. The method is not perfect, can’t always find a suggestion and sometimes finds too many and/or implausible suggestions, but it can help to speed up the process for a lot of the more obvious fault types.

## When all the opinions are collected

An “opinion” is just one person’s choice of “fault type”. Each Quest is designed to gather a maximum of 3 opinions for each record. When a record has 2 opinions that match each other, the record is considered to have a majority opinion and is “complete”. When every record has a majority opinion, the entire Quest is deemed to be “complete”. The Quest's “Status” page displays the Quest’s progress.

Sometimes a record gathers 3 completely differing opinions. At the end of the Quest, when every record has attained a maximum number of opinions, the records without a majority opinion are extracted to a spreadsheet and a process of adjudication is conducted. The “winning” opinions are fed back into to the Quest database.

When every record has either a majority or an adjudicated opinion the Quest is closed and the task of analysis commences.

The results of the analysis are presented and published in various formats and a variety of locations.
[The ORA website Insights page](https://openrepair.org/open-data/insights/)
[The ORDS Github repository](https://github.com/openrepair/data/tree/master/quests)
[The ORA Metabase instance](https://metabase.openrepair.org/public/dashboard/aa819192-2725-4a5e-b714-b2cc8195b01b)
[The Restart Project’s Workbench](https://restarters.net/workbench)

It is the results of analysis that is used to inform the next steps in terms of the action/campaign/policy roadmap.
