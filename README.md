# community-networks-monitoring-tools

---
This code is useful to recreate the results published in the paper *On the Technical and Social Structure of Community Networks*, In The First IFIP Internet of People Workshop, IoP, 2016 [IEEE link here](http://ieeexplore.ieee.org/document/7497253/) and [pdf here](https://ans.disi.unitn.it/users/maccari/assets/files/bibliography/IoP2016.pdf).

The same results are part of the deliverable D2.5 which you can find in the www.netcommons.eu website, that financed the development of this code.

---

Contains network topology and community analysis tools. All the code was produced in the netCommons project, each folder has its own Readme that explains what you can do with it, briefly:

1. fromdiff: contains a library and an interactive script to perform similarity matching on the "From" fields in a mailbox. With this code you can spot cases in which one person uses sligthly different emails in the same mailing list and merge them into one for further processing. You can try the aggregator on the piece of public mailing list that is included in the testdata/ folder, after you run the conversion script in the mailing-list-analyser/scripts/ folder (see the readme in mailing-list-analyser/)
2. mailing-list-analyser: find the most central, the most relevant people in a mailing list and detect the communities
3. fairgraph: the node re-assignment algorithm introduced in the extension to the paper mentioned (currently under review).

The tests folder contains simple code for you to test some basic functions and the testdata folder contains the required data.

Note the repo pulls code from two more repos, so execute `git submodule init; git submodule update` after checkout

# Known Issues

This code was generated in different moments, so it needs some work to make the style homogenous (which is not at the time). It was tested for graphs up to hundreds of nodes, so it focuses most on readability than efficiency.