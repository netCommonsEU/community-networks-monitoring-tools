#! /usr/bin/python
import sys
import mailbox
import mbparse

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'Usage: /mbparse.py mbox names_dictionary'
        sys.exit(1)

    mbox_file = sys.argv[1]
    dictionary = sys.argv[2]
    mailbox = mailbox.mbox(mbox_file)
    g = mbparse.parse_mbox_fragment(mailbox, dictionary)
    mbparse.get_ML_relevance(g)
    commmunities = mbparse.get_communities(g)
    mbparse.draw_community(g, commmunities,
                           save_file="/tmp/community_graph.graphml")
    mailbox.close()
