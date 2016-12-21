#! /usr/bin/python
import mailbox
import sys
import os
sys.path.insert(0, os.path.abspath("../mailing-list-analyser/"))
import mbparse
import networkx as nx
from Crypto.Hash import SHA256

if __name__ == "__main__":
    """ take as input a string, use it to hash the "From" fields
    as read from a mailing list, then save the graph in graphml format """
    if len(sys.argv) > 3:
        crypto_key = sys.argv[3]
    else:
        crypto_key = None
    print crypto_key
    mbox_file = sys.argv[1]
    dictionary = sys.argv[2]
    mailbox = mailbox.mbox(mbox_file)
    g = mbparse.parse_mbox_fragment(mailbox, dictionary)
    mailbox.close()
    if crypto_key:
        for node in g.nodes():
            h = SHA256.new(crypto_key)
            h.update(str(node))
            g = nx.relabel_nodes(g, {str(node): h.hexdigest()}, copy=False)
    nx.write_graphml(g, "/tmp/ninux-ml.xml")
