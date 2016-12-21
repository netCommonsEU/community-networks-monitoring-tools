#! /usr/bin/python
import sys
import os
import networkx as nx
sys.path.insert(0, os.path.abspath("../mailing-list-analyser/"))
import mbparse


if __name__ == "__main__":
    """ this script tests some analysis functions while
    taking as input a graphml file, and not a whole ML archive """

    if len(sys.argv) > 1:
        ml_graph_file = sys.argv[1]
    else:
        ml_graph_file = "../testdata/ninux-ml.xml"
    g = nx.read_graphml(ml_graph_file)
    mbparse.get_ML_relevance(g)
    communities = mbparse.get_communities(g)
    mbparse.draw_community(g, communities,
                           save_file="/tmp/community_graph.graphml")
