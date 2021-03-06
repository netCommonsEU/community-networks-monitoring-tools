# Copyright (C) 2016  Leonardo Maccari maccari@disi.unitn.it
# Author: Leonardo Maccari maccari@disi.unitn.it
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import email
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import community
import simplejson
import time
import re


def parse_mbox_fragment(mbox, names_dictionary):

    """ parse a mailbox fragment and build the community graph """
    mb_graph = nx.DiGraph()
    id_map = set()
    message_dict = {}
    people_dict = {}
    arrived_info = 0
    people_dict = {}
    try:
        f = open(names_dictionary, "r")
        people_dict = simplejson.load(f)
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
        from_field = unicode(message["From"],
                             'ISO-8859-2').encode('ascii', 'ignore')

        # the alias dictionary is in the form:
        # From_ascii_string: [[match_score, match_kind],
        #                     [name1, user1, domain1],
        #                     [name2, user2, domain2],
        #                     matching_From_ascii_string]

        if from_field in people_dict:
            from_field = people_dict[from_field][3]
        message_id = message['Message-ID']
        message_date = time.mktime(email.utils.parsedate(message["Date"]))
        if not earliest_message_date or message_date < earliest_message_date:
            earliest_message_date = message_date
            earliest_message_date_s = message["Date"]
        elif not latest_message_date or message_date > latest_message_date:
            latest_message_date = message_date
            latest_message_date_s = message["Date"]

        message_dict[message_id] = from_field
        if from_field not in id_map:
            id_map.add(from_field)
            mb_graph.add_node(from_field, emails=1, thread_started=0)
        else:
            num_emails = mb_graph.node[from_field]["emails"]
            mb_graph.node[from_field]["emails"] = num_emails + 1
        reply_user = ""
        try:
            replyTo = message['In-Reply-To']
            reply_user = message_dict[replyTo]
        except KeyError:
            mb_graph.node[from_field]["thread_started"] += 1

        if reply_user != "":
            found = False
            for neigh in mb_graph[reply_user]:
                if neigh == from_field:
                    mb_graph[reply_user][from_field]['weight'] += 1
                    arrived_info += 1
                    found = True
                    break
            if not found:
                # the link goes from the one that receives the response
                # to the one that responds
                mb_graph.add_edge(reply_user, from_field, weight=1)
                arrived_info += 1
    # il message-id e' unico di ogni messaggio
    # In-Reply-To e' l'id del messaggio a cui si risponde
    # nelle References c'e' la sequenza di messaggi fino a quello
    # nx.draw(mb_graph)
    # plt.show()
    out_degree_dict = {}
    in_degree_dict = {}
    info_rank = {}
    email_sent = {}
    lone_nodes = 0
    for n in mb_graph:
        out_degree_dict[n] = mb_graph.out_degree(n, weight="weight")
        ts = mb_graph.node[n]["thread_started"]
        in_degree_dict[n] = mb_graph.in_degree(n, weight="weight")
        if in_degree_dict[n] == 0:
            lone_nodes += 1
        email_sent[n] = ts + in_degree_dict[n]
        # all the information sent by node n / total information sent
        info_rank[n] = float(out_degree_dict[n])/arrived_info
    c = nx.betweenness_centrality(nx.Graph(mb_graph))

    print "=============== Summary ========================"
    print "# tot num messages", len(message_dict)
    print "# tot num replies", arrived_info
    print "# first email:", earliest_message_date_s
    print "# last email:", latest_message_date_s
    print "# num senders:", len(mb_graph)
    print "# num senders without answer:", lone_nodes
    print "======================================="
    print
    print "=============== Centrality ========================"

    print "# node".ljust(30), ",", "centrality".ljust(10)
    for p in sorted(c.items(), key=lambda x: -x[1]):
        print p[0].ljust(30), ",", str(p[1]).ljust(10)

    return mb_graph


def get_ML_relevance(graph):
    """ Compute the relevance of each person in the mailing list as the
    normalized sum of received answers """

    received_answers = defaultdict(int)
    tot_w = 0
    for node in graph.nodes(data=True):
        for e in graph.in_edges(node[0], data=True):
            received_answers[node[0]] += e[2]['weight']
            tot_w += e[2]['weight']
    print
    print "=============== ML Relevance ========================"
    print "# person".ljust(30), ",", "relevance".ljust(10)
    s_l = sorted(received_answers.items(), key=lambda x: -x[1])
    for p, w in s_l:
        print p.ljust(30), ",", str(float(w)/tot_w).ljust(10)
    print ""
    print ""
    print "# person".ljust(30), ",", "cumulative  relevance".ljust(10)
    for idx, (p, w) in enumerate(s_l):
        print p.ljust(30), ",", str(float(sum([x[1]
                                    for x in s_l[:idx+1]]))/tot_w).ljust(10)
    print ""
    print ""


def get_communities(di_graph):

    """ compute the communities in the social network, using the Louvain method
    """

    # community detection works on undirected graphs, so we pick for each
    # neighbor couple the link with the highest weight. A person A that
    # receives a lot of information (i.e. asnwer to a lot of emails) from
    # a person B, is considere in B's community.
    graph = nx.Graph()
    for node in di_graph.nodes():
        graph.add_node(node)
        for neigh in di_graph.neighbors(node):
            edge_weight = di_graph.get_edge_data(node, neigh)["weight"]
            reverse_weight_data = di_graph.get_edge_data(neigh, node)
            if not reverse_weight_data:
                reverse_weight = 0
            else:
                reverse_weight = reverse_weight_data["weight"]
            graph.add_edge(node, neigh,
                           {"weight": max(edge_weight, reverse_weight)})

    partition = community.best_partition(graph)
    parition_score = community.modularity(partition, graph)
    print "=============== Community Partitions ========================"
    print "# parition modularity:", parition_score
    for node in partition:
        node_email = re.search(r'[\w\.-]+@[\w\.-]+',
                               node)
        if node_email:
            print node_email.group(0), ",", partition[node]
        else:
            print node, ",", partition[node]
    return partition


def draw_community(graph, partition, save_file="", plot_tables=True):
    """ draw the induced community graph, without isolated nodes and with
    several positioning types """

    # remove isolated nodes
    draw_graph = community.induced_graph(partition, graph)
    if save_file:
        nx.write_graphml(draw_graph, save_file)
    for node in draw_graph.nodes()[:]:
        if not draw_graph.neighbors(node):
            draw_graph.remove_node(node)

    # build a map: community -> [node list]
    com_members = defaultdict(list)
    max_community_size = 0
    for com in set(partition.values()):
        list_nodes = [nodes for nodes in partition.keys()
                      if partition[nodes] == com]
        if len(list_nodes) > 1:
            com_members[com] = list_nodes
            if len(list_nodes) > max_community_size:
                max_community_size = len(list_nodes)

    # define arrays of colors, labels and node size
    nodelist = draw_graph.nodes()
    nodesize = []
    nodelabels = {}
    for node in draw_graph.nodes():
        nodesize.append(300+1000*len(com_members[node])/max_community_size)
    sorted_com_names = {}
    for idx, com in enumerate(sorted(com_members.items(),
                                     key=lambda x: len(x[1]))):
        sorted_com_names[idx] = com[0]

    for newlabel, oldlabel in sorted_com_names.items():
        nodelabels[oldlabel] = newlabel

    link_color = []
    edge_weight_max = max([x[2]["weight"]
                          for x in draw_graph.edges(data=True)])
    for link in draw_graph.edges(data=True):
        link_color.append(float(link[2]["weight"])/edge_weight_max)
    print
    print "=============== Tables ========================"
    if plot_tables:  # just plot a LaTeX table
        print "Community & Size \\\\"
        for node, com in sorted_com_names.items():
            print node, " & ", len(com_members[com]), "\\\\"
        print
        print
        print "% community interactions"
        print " & ", " & ".join(str(node) for node in sorted_com_names), "\\\\"
        for node, com in sorted_com_names.items():
            print node,
            for neigh in sorted_com_names.values():
                try:
                    edge = draw_graph[com][neigh]
                    e = edge["weight"]
                except KeyError:
                    e = 0
                print " & ", e,
            print "\\\\"

    pos = nx.circular_layout(draw_graph)
    nx.draw(draw_graph, pos=pos, node_list=nodelist, node_size=nodesize,
            labels=nodelabels, edge_list=draw_graph.edges(),
            edge_color=link_color, with_labels=True,
            edge_cmap=plt.cm.Blues, width=5, font_size=15)
    plt.show()
