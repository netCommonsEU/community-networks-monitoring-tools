#! /usr/bin/python
import sys
import mailbox
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import re
import chardet



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
                            y.encode('ascii', 'ignore'))
                    if differenceScore < r:
                        differenceScore = r
            fromDiff[left].append((r, right))
    for s,d in fromDiff.items():
        mindiff =  sorted(d, key=lambda x: x[0])[0]
        if mindiff[0] > 0.7:
            print s, mindiff
     
def parseMboxFragment(mbox):
    mbGraph = nx.DiGraph()
    idMap = set()
    messageDict = {}
    peopleDict = {}
    arrivedInfo = 0 #FIXME rename all this "message" in "info"
    for message in mbox:
        fromField = unicode(message["From"], 
                'ISO-8859-2').encode('utf-8', 'ignore')
        peopleDict[fromField] = parseAddress(fromField)
        messageID = message['Message-ID']
        messageDict[messageID] = fromField
        if fromField not in idMap:
            idMap.add(fromField)
            mbGraph.add_node(fromField, emails=1, threadStarted=0)
        else:
            numEmails = mbGraph.node[fromField]["emails"]
            mbGraph.node[fromField]["emails"] = numEmails + 1
        try:
            replyTo = message['In-Reply-To']
            replyUser = messageDict[replyTo]
            found = False
            for neigh in mbGraph[fromField]:
                if neigh == replyUser:
                    mbGraph[replyUser][fromField]['weight'] += 1
                    arrivedInfo += 1
                    found = True
                    break
            if not found:
                # the link goes from the one that receives the response
                # the one that responds
                mbGraph.add_edge(replyUser, fromField, weight = 1)
        except KeyError: 
            mbGraph.node[fromField]["threadStarted"] += 1 
    # il message-id e' unico di ogni messaggio
    # In-Reply-To e' l'id del messaggio a cui si risponde
    # nelle References c'e' la sequenza di messaggi fino a quello
    nx.draw(mbGraph)
    #plt.show()
    outDegreeDict = {}
    inDegreeDict = {}
    infoRank = {}
    emailSent = {}
    for n in mbGraph:
        outDegreeDict[n] = mbGraph.out_degree(n, weight="weight")
        try:
            ts = mbGraph[n]["threadStarted"]
        except KeyError:
            ts = 0
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
    for k,v in sorted(infoRank.items(), key=lambda x: x[1])[-10:]:
        print k,v

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: /mbparse.pypython mbox'
        sys.exit(1)

    mboxFile = sys.argv[1]
    mbox = mailbox.mbox(mboxFile)
    parseMboxFragment(mbox)
    mbox.close()


