#! /usr/bin/python
import sys
import mailbox
import  email 
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import community
import simplejson
import datetime
from fromdiff import fromdiff
import time

#FIXME make this dynamic

def parseMboxFragment(mbox, names_dictionary):
    mbGraph = nx.DiGraph()
    idMap = set()
    messageDict = {}
    peopleDict = {}
    arrivedInfo = 0
    peopleDict = {}
    try:
        f = open(names_dictionary, "r")
        peopleDict = simplejson.load(f)
    except IOError:
        print "The json file", names_dictionary, "can not be opened"
    except:
        print "The json file", names_dictionary, "has some format problems"

    earliest_message_date = ""
    earliest_message_date_s = ""
    latest_message_date = ""
    latest_message_date_s = ""
    for message in mbox:
        # ascii is the only way to have tk draw the graph, not utf-8
        fromField = unicode(message["From"],
                'ISO-8859-2').encode('ascii', 'ignore')

        # the alias dictionary is in the form:
        # From_ascii_string: [[match_score, match_kind],
        #                     [name1, user1, domain1],
        #                     [name2, user2, domain2],
        #                     matching_From_ascii_string]

        if fromField in peopleDict:
            fromField = peopleDict[fromField][3]
        messageID = message['Message-ID']
        messageDate = time.mktime(email.utils.parsedate(message["Date"]))
        if not earliest_message_date or messageDate < earliest_message_date:
            earliest_message_date = messageDate
            earliest_message_date_s = message["Date"]
        elif not latest_message_date or messageDate > latest_message_date:
            latest_message_date = messageDate
            latest_message_date_s = message["Date"]

        messageDict[messageID] = fromField
        if fromField not in idMap:
            idMap.add(fromField)
            mbGraph.add_node(fromField, emails=1, threadStarted=0)
        else:
            numEmails = mbGraph.node[fromField]["emails"]
            mbGraph.node[fromField]["emails"] = numEmails + 1
        replyUser = ""
        try:
            replyTo = message['In-Reply-To']
            replyUser = messageDict[replyTo]
        except KeyError:
            mbGraph.node[fromField]["threadStarted"] += 1

        if replyUser != "":
            found = False
            for neigh in mbGraph[replyUser]:
                if neigh == fromField:
                    mbGraph[replyUser][fromField]['weight'] += 1
                    arrivedInfo += 1
                    found = True
                    break
            if not found:
                # the link goes from the one that receives the response
                # to the one that responds
                mbGraph.add_edge(replyUser, fromField, weight=1)
                arrivedInfo += 1
    # il message-id e' unico di ogni messaggio
    # In-Reply-To e' l'id del messaggio a cui si risponde
    # nelle References c'e' la sequenza di messaggi fino a quello
    # nx.draw(mbGraph)
    # plt.show()
    outDegreeDict = {}
    inDegreeDict = {}
    infoRank = {}
    emailSent = {}
    lone_nodes = 0
    for n in mbGraph:
        outDegreeDict[n] = mbGraph.out_degree(n, weight="weight")
        ts = mbGraph.node[n]["threadStarted"]
        inDegreeDict[n] = mbGraph.in_degree(n, weight="weight")
        if inDegreeDict[n] == 0:
            lone_nodes += 1
        emailSent[n] = ts + inDegreeDict[n]
        # all the information sent by node n / total information sent
        infoRank[n] = float(outDegreeDict[n])/arrivedInfo
    c = nx.betweenness_centrality(nx.Graph(mbGraph))
    print "# node".ljust(30), ",", "centrality".ljust(10)
    for p in sorted(c.items(), key=lambda x: -x[1]):
        parsed_fields = fromdiff.parse_address(p[0])
        from_f = parsed_fields[1] + "@" + parsed_fields[2]
        print from_f.ljust(30), ",", str(p[1]).ljust(10)
    print "# tot num messages", len(messageDict)
    print "# tot num replies", arrivedInfo
    print "# first email:", earliest_message_date_s
    print "# last email:", latest_message_date_s
    print "# num senders:", len(mbGraph)
    print "# num senders without answer:", lone_nodes

    return mbGraph


def getMLRelevance(graph):
    received_anwers = defaultdict(int)
    tot_w = 0
    for node in graph.nodes(data=True):
        parsed_fields = fromdiff.parse_address(node[0])
        from_f = parsed_fields[1] + "@" + parsed_fields[2]
        for e in graph.in_edges(node[0], data=True):
            received_anwers[from_f] += e[2]['weight']
            tot_w += e[2]['weight']
    print "# person".ljust(30), ",", "relevance".ljust(10)
    s_l = sorted(received_anwers.items(), key=lambda x: -x[1])
    for p, w in s_l:
        print p.ljust(30), ",", str(float(w)/tot_w).ljust(10)
    print ""
    print ""
    print "# person".ljust(30), ",", "cumulative  relevance".ljust(10)
    for idx, (p, w) in enumerate(s_l):
        print p.ljust(30), ",", str(float(sum([x[1] for x in s_l[:idx+1]]))/tot_w).ljust(10)
    print ""
    print ""


def getCommunities(diGraph):

    # community detection works on undirected graphs, so we pick for each
    # neighbor couple the link with the highest weight. A person A that
    # receives a lot of information (i.e. asnwer to a lot of emails) from
    # a person B, is considere in B's community.
    graph = nx.Graph()
    for node in diGraph.nodes():
        graph.add_node(node)
        for neigh in diGraph.neighbors(node):
            edge_weight = diGraph.edges(node, neigh)[0][2]["weight"]
            try:
                reverse_weight = diGraph.edges(neigh, node)[0][2]["weight"]
            except IndexError:
                reverse_weight = 0
            graph.add_edge(node, neigh,
                           {"weight": max(edge_weight, reverse_weight)})

    partition = community.best_partition(graph)
    parition_score = community.modularity(partition, graph)
    print "# parition modularity:", parition_score
    for node in partition:
        name, user, domain = fromdiff.parse_address(node)
        print "<"+user+"@"+domain+">", ",", partition[node]
    return partition


def drawCommunity(graph, partition, saveFile="", plotTables=True):
    """ draw the induced community graph, without isolated nodes and with
    several positioning types """

    # remove isolated nodes
    drawGraph = community.induced_graph(partition, graph)
    if saveFile:
        nx.write_graphml(drawGraph, saveFile)
    for node in drawGraph.nodes()[:]:
        if not drawGraph.neighbors(node):
            drawGraph.remove_node(node)

    # build a map community -> [node list]
    comMembers = defaultdict(list)
    max_community_size = 0
    for com in set(partition.values()):
        list_nodes = [nodes for nodes in partition.keys()
                      if partition[nodes] == com]
        comMembers[com] = list_nodes
        if len(list_nodes) > max_community_size:
            max_community_size = len(list_nodes)

    # define arrays of colors, labels and node size
    nodelist = drawGraph.nodes()
    nodesize = []
    nodelabels = {}
    for node in drawGraph.nodes():
        nodesize.append(300+1000*len(comMembers[node])/max_community_size)
        nodelabels[node] = len(comMembers[node])
    sortedComNames = {}
    for idx, com in enumerate(sorted(filter(lambda x:len(x[1])>1, comMembers.items()),
        key=lambda x: len(x[1]))):
        sortedComNames[idx] = com[0]

    link_color = []
    edge_weight_max = max([x[2]["weight"] for x in drawGraph.edges(data=True)])
    for link in drawGraph.edges(data=True):
        link_color.append(float(link[2]["weight"])/edge_weight_max)
    if plotTables:
        print "Community & Size \\\\"
        for node, com in sortedComNames.items():
            print node, " & ", len(comMembers[com]), "\\\\"
        print
        print
        print " & ", " & ".join(str(node) for node in sortedComNames), "\\\\"
        for node, com in sortedComNames.items():
            print node,
            for neigh in sortedComNames.values():
                edge = drawGraph[com][neigh]
                print " & ", edge["weight"],
            print "\\\\"



    pos = nx.circular_layout(drawGraph)
    nx.draw(drawGraph, pos=pos, node_list=nodelist, node_size=nodesize,
            labels=nodelabels, edge_list=drawGraph.edges(),
            edge_color=link_color, with_labels=True,
            edge_cmap=plt.cm.Blues, width=5, font_size=15)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'Usage: /mbparse.py mbox names_dictionary'
        sys.exit(1)

    mboxFile = sys.argv[1]
    names_dictionary = sys.argv[2]
    mbox = mailbox.mbox(mboxFile)
    g = parseMboxFragment(mbox, names_dictionary)
    getMLRelevance(g)
    commmunities = getCommunities(g)
    drawCommunity(g, commmunities, saveFile="/tmp/community_graph.graphml")
    #saveJSON(mbox)
    mbox.close()


