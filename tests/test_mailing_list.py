#! /usr/bin/python
import mailbox
import sys
import os
sys.path.insert(0, os.path.abspath("../mailing-list-analyser/"))
import mbparse

if __name__ == "__main__":
    if len(sys.argv) == 1:
        mbox_file = "../testdata/wireless-12-2016.txt"
        dictionary = "../testdata/aliases.xml"
    else:
        mbox_file = sys.argv[1]
        dictionary = sys.argv[2]
    mailbox = mailbox.mbox(mbox_file)
    g = mbparse.parse_mbox_fragment(mailbox, dictionary)
    mbparse.get_ML_relevance(g)
    communities = mbparse.get_communities(g)
    mbparse.draw_community(g, communities,
                           save_file="/tmp/community_graph.graphml")
    mailbox.close()
