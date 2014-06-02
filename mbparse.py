#! /usr/bin/python
import sys
import mailbox
import networkx as nx
import matplotlib.pyplot as plt

def parseMboxFragment(mbox):
    mbGraph = nx.Graph()
    idMap = set()
    messageDict = {}
    for message in mbox:
        fromField = message['From']
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
    nx.draw(mbGraph)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: /mbparse.pypython mbox'
        sys.exit(1)

    mboxFile = sys.argv[1]
    mbox = mailbox.mbox(mboxFile)
    parseMboxFragment(mbox)


