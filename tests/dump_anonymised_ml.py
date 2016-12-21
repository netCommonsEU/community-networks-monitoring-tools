#! /usr/bin/python
import mailbox
import sys
import os
sys.path.insert(0, os.path.abspath("../mailing-list-analyser/"))
import mbparse
import networkx as nx
from Crypto.Hash import SHA256
import re


if __name__ == "__main__":
    """ take as input a string, use it to hash the "From" fields
    as read from a mailing list, then save the graph in graphml format """
    if len(sys.argv) > 3:
        crypto_key = sys.argv[3]
    else:
        crypto_key = None
    mbox_file = sys.argv[1]
    dictionary = sys.argv[2]
    mailbox = mailbox.mbox(mbox_file)
    g = mbparse.parse_mbox_fragment(mailbox, dictionary)
    mailbox.close()
    gg = g.copy()
    #if crypto_key:
    #    for node in g.nodes():
    #        email = re.search(r'[\w\.-]+@[\w\.-]+',
    #                          node).group(0)
    #        h = SHA256.new(crypto_key)
    #        h.update(str(email))
    #        g = nx.relabel_nodes(g, {str(node): h.hexdigest()}, copy=False)
    ggg = nx.convert_node_labels_to_integers(g)
    import code
    code.interact(local=locals())
    c_g = mbparse.get_communities(g)
    c_ggg = mbparse.get_communities(ggg)
    c_g_s = [len(x) for x in [filter(lambda y: y[1] == k, c_g.items()) for k in set(c_g.values())]]
    c_ggg_s = [len(x) for x in [filter(lambda y: y[1] == k, c_ggg.items()) for k in set(c_ggg.values())]]
    import code
    code.interact(local=locals())
    nx.write_graphml(g, "/tmp/anonymised-ml.xml")
