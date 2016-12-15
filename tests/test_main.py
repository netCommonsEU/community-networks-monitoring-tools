#! /usr/bin/python
import mailbox
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import mbparse

if __name__ == "__main__":
    mbox_file = "../testdata/wireless-12-2016.txt"
    dictionary = "../testdata/aliases.xml"
    mailbox = mailbox.mbox(mbox_file)
    g = mbparse.parse_mbox_fragment(mailbox, dictionary)
    mbparse.get_ML_relevance(g)
    commmunities = mbparse.get_communities(g)
    mbparse.draw_community(g, commmunities,
                           save_file="/tmp/community_graph.graphml")
    mailbox.close()
