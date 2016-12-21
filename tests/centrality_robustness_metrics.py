#!/usr/bin/python
import sys
import os
import getopt
import glob
sys.path.insert(0, os.path.abspath("../centrality-robustness-metrics/"))
import owner_graph_metrics as ogm
from owner_graph_metrics import dataObject, dd1, dd2, dd3, dd4, dd5

data = ogm.dataObject()

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:n:d:p:")
    except getopt.GetoptError, err:
        print >> sys.stderr,  str(err)
        sys.exit(1)
    for option, v in opts:
        if option == "-p":
            """ load a pickle file saved with save() """
            try:
                data.initialize(v)
            except IOError:
                print "could not read data file"
                sys.exit(1)
            continue
        if option == "-n":
            """ use an alias dictionary """
            data.initialize_names_dictionary(v)
            data.dump_graphs(data)
            continue
        if option == "-d":
            data.dump_db(v, data)
            continue
        if option == "-f":
            # load a bunch of graphml files (multiple -f is ok
            # as long as you put them betweej ticks to prevent
            # shell expansion, like:
            # ./centrality_robustness_metrics.py \
            #        -f '../testdata/xml/FFGraz/*.xml' \
            #        -f '../testdata/xml/FFWien/*.xml'

            file_list = glob.glob(v)
            data.initialize_from_files(file_list)
            continue

    print "You see nothing? check the source file to",\
          "enable the functions you need"

    # example actions to reproduce D2.5 graphs:
    # use with ./centrality_robustness_metrics.py \
    #       -f '../testdata/xml/FFGraz/*.xml' -f '../testdata/xml/FFWien/*.xml'
    # for net in data.routeData:
    #    data.computePrefAttachTrend(net)

    # the next functions are example of data generation, all them need
    # to be decommented one by one and then use:
    #    ./centrality_robustness_metrics.py -f ../testdata/xml/ninux/ninux0.xml

    # get the ownership distribution from the ninux0.xml graph
    # data.get_owner_distribution(data.routeData["ninux"][1]["Graph"], False)

    # plot the "owner robustness", need a graph with annotated ownership
    # data.getOwnerRobustness(data.routeData["ninux"][1]["Graph"])

    # plot the owner centrality
    # data.getOwnerCentrality(data.routeData["ninux"][1]["Graph"])

    # plot the owner-to-owner centrality
    # data.getOwnerToOwnerCentrality(data.routeData["ninux"][1]["Graph"])
