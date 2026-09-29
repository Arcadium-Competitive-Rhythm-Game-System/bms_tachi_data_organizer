# BMS Tachi Data Organizer

Using a lot of data from Tachi ([website](https://boku.tachi.ac/) | [repository](https://github.com/zkldi/Tachi)), these python scripts and CSVs generated from the scripts are the initial data for a future project known as *Arcadium - BMS Battle* (working name).

These scripts work with chart Sieglinde values and organize those values into ELO, which get further divided into competitive ranks (Bronze -> Grandmaster).

### What is a Sieglinde?
A Sieglinde is an arbitrary number that goes from 1 to 41. A higher number means the chart is harder to clear. It is important to note, Sieglinde ONLY takes into account clear on a particular type of gauge, not how well the player performed in terms of score or accuracy. Tachi divides these into Easy Clear ratings, and Hard Clear ratings. As such, a separate ELO is derived for either clear type.

### What is Arcadium?
It is a WIP project that involves players working their way through an ELO system, being given random charts roughly around their ELO, and having to clear the chart in a given amount of time. Depending on if they do so, they either win or lose the "match". Both players and charts have ELO, and in the system, both players and charts can gain or lose ELO. These scripts help facilitate an initial database using various Tachi datasets.