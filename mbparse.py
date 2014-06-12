#! /usr/bin/python
import sys
import mailbox
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import re
import chardet
import community
import diffFrom
import simplejson



# my files
from miscLibs import *

def clusterNames(peopleDict):
    """ get a dictionary with id:["real name","email"] and compare
    all the combinations between name and email for every couple
    of users and find the combination with highest similarity """

    fromDiff = defaultdict(list)
    for left,firstData in peopleDict.items():
        for right,secondData in peopleDict.items():
            differenceScore = 0
            #exclude domain from comparisons
            for x in firstData[:-1]:
                for y in secondData[:-1]:
                    r = diffString(x.encode('ascii', 'ignore'),
                            y.encode('ascii', 'ignore'), algorithm="WW")
                    if differenceScore < r:
                        differenceScore = r
            fromDiff[left].append((r, right))
    for s,d in fromDiff.items():
        mindiff =  sorted(d, key=lambda x: x[0])[0]
        if mindiff[0] > 0.3:
            print s, mindiff
     
def parseMboxFragment(mbox):
    mbGraph = nx.DiGraph()
    idMap = set()
    messageDict = {}
    peopleDict = {}
    arrivedInfo = 0 
    for message in mbox:
        #FIXME ascii is the only way to have tk drow the graph, not utf-8
        # but this can interfere with names clustering
        fromField = unicode(message["From"], 
                'ISO-8859-2').encode('ascii', 'ignore')
        peopleDict[fromField] = parseAddress(fromField)
        messageID = message['Message-ID']
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
                # the one that responds
                mbGraph.add_edge(replyUser, fromField, weight = 1)
                arrivedInfo += 1
    # il message-id e' unico di ogni messaggio
    # In-Reply-To e' l'id del messaggio a cui si risponde
    # nelle References c'e' la sequenza di messaggi fino a quello
    nx.draw(mbGraph)
    #plt.show()
    #FIXME we have to apply clusterNames before the rest
    #clusterNames(peopleDict)
    outDegreeDict = {}
    inDegreeDict = {}
    infoRank = {}
    emailSent = {}
    for n in mbGraph:
        outDegreeDict[n] = mbGraph.out_degree(n, weight="weight")
        print n, outDegreeDict[n], arrivedInfo
        ts = mbGraph.node[n]["threadStarted"]
        inDegreeDict[n] = mbGraph.in_degree(n, weight="weight") 
        emailSent[n] = ts + inDegreeDict[n]
        #all the information sent by node n / total information sent
        infoRank[n] = float(outDegreeDict[n])/arrivedInfo
    print
    print "Sent information"
    print
    for k,v in sorted(outDegreeDict.items(), key=lambda x: x[1])[-10:]:
        print k,v
    print
    print "Received Information"
    print
    for k,v in sorted(inDegreeDict.items(), key=lambda x: x[1])[-10:]:
        print k,v
    print
    print "Sent emails"
    print
    for k,v in sorted(emailSent.items(), key=lambda x: x[1])[-10:]:
        print k,v
    print
    print "Info ranking"
    print
    infoSum = 0
    for k,v in sorted(infoRank.items(), key=lambda x: x[1]):
        print k,v
        infoSum += v
    print "InfoSum", infoSum


def getPartitions(mbGraph):
    unMbGraph = nx.Graph()
    for n in mbGraph.nodes():
        unMbGraph.add_node(n)
        for neigh in mbGraph[n]:
            unMbGraph.add_node(neigh)
            if neigh in unMbGraph[n]:
                unMbGraph.edges(n,neigh)["weight"] \
                        += mbGraph[n][neigh]["weight"]
            else:
                unMbGraph.add_edge(n, neigh, 
                        weight=mbGraph[n][neigh]["weight"])

    partition = community.best_partition(unMbGraph)
    communities =  set(partition.values())
    drawGraph = nx.Graph()
    comMembers = defaultdict(list)

    maxSize = 0
    nodeLabels = {}
    for com in communities :
        list_nodes = [nodes for nodes in partition.keys()
                                    if partition[nodes] == com]
        comMembers[com] = list_nodes
        drawGraph.add_node(com, size=len(list_nodes))
        nodeLabels[com] = len(list_nodes)
        if len(list_nodes) > maxSize:
            maxSize = len(list_nodes)
    maxLinks = 0
    for c,l in [(c,l) for (c,l) in sorted(comMembers.items(), key=lambda x: len(x[1]))]:
        print 
        cRank = 0
        for n in l:
            cRank += infoRank[n]
        print "XXXXXXXXXX", cRank, "XXXXXXXXXX"
        for u in [user for user in sorted(l, key=lambda x: infoRank[x])]:
            print u

    for n in unMbGraph.nodes():
        c1 = partition[n]
        for neigh in unMbGraph[n]:
            c2 = partition[neigh]
            if c2 in drawGraph[c1]:
                drawGraph[c1][c2]["weight"] += 1
                if drawGraph[c1][c2]["weight"] > maxLinks:
                    maxLinks = drawGraph[c1][c2]["weight"]
            else:
                drawGraph.add_edge(c1,c2,weight=1) 
    plt.clf()
    nodelist = drawGraph.nodes()
    nodesize = [150+300*drawGraph.node[s]["size"]/maxSize for s in nodelist]
    linkColor = [float(l[2]["weight"])/len(unMbGraph.edges()) for l in \
            drawGraph.edges(data=True)]
    nx.draw(drawGraph, node_list=nodelist, node_size=nodesize, 
        labels=nodeLabels, edge_list=drawGraph.edges(), 
        edge_color=linkColor, edge_cmap=plt.cm.Blues)
    plt.show()

def saveJSON(mbox):
    """ This function produces a json file with a list of the From: emails
    formatted according to the input needed by the diffFrom script I use
    to aggregate the emails"""
    fromList = []
    for message in mbox:
        #FIXME ascii is the only way to have tk drow the graph, not utf-8
        # but this can interfere with names clustering
        fromField = unicode(message["From"], 
                'ISO-8859-2').encode('ascii', 'ignore')
        [name, user, domain] = parseAddress(fromField)
        fromList.append('"'+name+'"'+" <"+user+'@'+domain+'>')
    outFile = "/tmp/fromlist.json"
    f = open(outFile, "w")
    simplejson.dump(fromList, f)
    f.close()
     

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: /mbparse.pypython mbox'
        sys.exit(1)

    mboxFile = sys.argv[1]
    mbox = mailbox.mbox(mboxFile)
    #parseMboxFragment(mbox)
    saveJSON(mbox)
    mbox.close()


