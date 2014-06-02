#! /usr/bin/python
import sys
import mailbox
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import re



# my files
from miscLibs import *


def parseMboxFragment(mbox):
    mbGraph = nx.Graph()
    idMap = set()
    messageDict = {}
    peopleDict = {}
    for message in mbox:
        fromField = message['From']
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
                    #interactions = mbGraph.node(fromField)[replyUser]['weight']
                    mbGraph[fromField][replyUser]['weight'] += 1
                    found = True
                    break
            if not found:
                mbGraph.add_edge(fromField, replyUser, weight = 1)
        except KeyError: 
            mbGraph.node[fromField]["threadStarted"] += 1 
    # il message-id e' unico di ogni messaggio
    # In-Reply-To e' l'id del messaggio a cui si risponde
    # nelle References c'e' la sequenza di messaggi fino a quello
    #nx.draw(mbGraph)
    #plt.show()

    fromDiff = defaultdict(list)
    for left,firstData in peopleDict.items():
        for right,secondData in peopleDict.items():
            differenceScore = 0
            #exclude domain from comparisons
            for x in firstData[:-1]:
                for y in secondData[:-1]:
                    r = diffString(x, y)
                    if differenceScore < r:
                        differenceScore = r
            fromDiff[left].append((r, right))
    for s,d in fromDiff.items():
        mindiff =  sorted(d, key=lambda x: x[0])[0]
        if mindiff[0] > 0.7:
            print s, mindiff
            

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: /mbparse.pypython mbox'
        sys.exit(1)

    mboxFile = sys.argv[1]
    mbox = mailbox.mbox(mboxFile)
    parseMboxFragment(mbox)
    mbox.close()


