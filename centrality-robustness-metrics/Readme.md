# Network Evolution

the network evolution graphs used to test Pref. Attachment hipothesis are
done with the this code.

Check the centrality_robustness_metrics.py in the tests folder, enable the data.computePrefAttachTrend function and run (see comments in the source):

./main.py -f '../testdata/xml/FFGraz/\*.xml' -f '../testdata/xml/FFWien/\*.xml'

in the testdata folder you can find all the graphs that represent the
FF networks in the period of observation.

# Ownership data
For the ownership and robustness graphs, you can check the centrality_robustness_metrics.py script in the tests/ folder for the
functions that generate all the graphs, and the ninux0.xml graph that
contains an anonymised graphml of the ninux network.

For the social network graphs check the ./test_mailing_list_graph.py in
the tests folder. That script uses the anonymised mailing list data file
present in the testdata/ folder and does the community detection.
