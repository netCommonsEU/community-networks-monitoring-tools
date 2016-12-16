from collections import defaultdict
import cPickle as pk
import simplejson
import re
import networkx as nx
from Crypto.Hash import SHA256

try:
    import key
    crypto_key = key.crypto_key
except:
    ImportError
    print "You don't have a crypo key file included, using default one"
    crypto_key = "12345"
    pass


# constants for spacing printouts
long_align_space = 30

# these module-level functions are needed or else I can
# not pickle the data structure


def dd1():
    return defaultdict(list)


def dd2():
    return defaultdict(dd1)


def dd3():
    return defaultdict(dd2)


def dd4():
    return defaultdict(dd3)


def dd5():
    return defaultdict(dd4)


class dataObject:
    """ This class is used to store and load pickle files """
    def __init__(self):
        self.scanTree = dd2()
        self.rawData = dd2()
        self.dataSummary = dd3()
        self.dumpFile = ""
        self.routeData = dd5()
        self.etxThreshold = -1
        self.namesDictionary = {}

    def initialize(self, fileName):
        self.dumpFile = fileName
        try:
            f = open(self.dumpFile, "r")
        except IOError:
            print "could not load", self.dumpFile
            raise
        d = pk.load(f)
        self.scanTree = d.scanTree
        self.rawData = d.rawData
        self.dataSummary = d.dataSummary
        self.routeData = d.routeData
        f.close()

    def initialize_names_dictionary(self, file_name):
        try:
            namesFile = open(file_name, "r")
        except IOError:
            print "ERROR: Could not load the name dictionary file", file_name
            return
        try:
            self.namesDictionary = simplejson.load(namesFile)
        except simplejson.JSONDecodeError:
            print "ERROR: could not parse the JSON names file"
        if not namesFile.closed:
            namesFile.close()
        self.email_aliases = {}
        for e in self.namesDictionary.items():
            # merge aliases into unique names
            alias_email = re.search(r'[\w\.-]+@[\w\.-]+',
                                    e[0]).group(0)
            unique_email = e[1][2][1] + "@" + e[1][2][2]
            self.email_aliases[alias_email] = unique_email

    def save(self, fileName):
        f = open(fileName, "w")
        pk.dump(self, f)
        f.close()

    def printSummary(self):
        logString = ""
        for net in self.scanTree:
            logString += "===== "+net+" =====\n"
            logString += "scans: " + str(len(self.dataSummary[net]))
            logString += "\n"
            logString += "\n"
            # print the header
            for sid in self.dataSummary[net]:
                logString += str("ID").ljust(4)
                for label in self.dataSummary[net][sid]:
                    logString += label[0].ljust(label[1]) + " "
                logString += "\n"
                break
            # print the data
            for sid in sorted(self.dataSummary[net]):
                logString += str(sid).ljust(4)
                for key, value in self.dataSummary[net][sid].items():
                    logString += str(value).ljust(key[1]) + " "
                logString += "\n"
        logString += "\n\nETX threshold:" + str(self.etxThreshold)

        return logString


def get_owner_distribution(graph, namesDictionary, silent=True):
    """ the namesDictionary is derived from "From" fields taken from
    parsing a mailing list mbox. It is in the form:
    {
        "name surname <user@domain>": [
            [
                match score, #  (1=high)
                "email->email" # what matches
            ],
            [ # clean values for candidate element
                "namesurname", # name stripepd of any non text char
                "user",
                "domain"
            ],
            [ # clean values for best match
                "namesurname2",
                "user2",
                "domain2"
            ],
            "name2 surname2 <user2@domain2>"
        ],
    see the fromdiff library:
    """

    # two helper structures
    nodeOwner = {}  # node -> owner
    ownerNodes = defaultdict(list)  # owner -> [nodes]

    for n in graph.nodes(data=True):
        node_email = re.search(r'[\w\.-]+@[\w\.-]+',
                               n[1]['email']).group(0)
        nodeOwner[n[0]] = node_email
        for e in namesDictionary.values():
            # merge aliases into unique names
            db_email = e[1][1] + "@" + e[1][2]
            if db_email == node_email:
                alias_email = e[2][1] + "@" + e[2][2]
                nodeOwner[n[0]] = alias_email
                break
        ownerNodes[nodeOwner[n[0]]].append(n[0])

    if not silent:
        print "# owner".rjust(long_align_space), ",",\
              "owned nodes".rjust(long_align_space)
        for owner, nodes in sorted(ownerNodes.items(),
                                   key=lambda(x): -len(x[1])):
            print owner.rjust(30), ",",  str(len(nodes)).rjust(30)
        print ""
        print ""

    return ownerNodes, nodeOwner


def dump_graphs(data, graphNumber=0):
    """ this function dumps in the /tmp/ folder a number of graphs in edgelist
    format """

    for net in data.routeData:
        scanIdList = data.routeData[net].keys()
        for i in range(len(scanIdList)):
            if not graphNumber or i < graphNumber:
                g = data.routeData[net][scanIdList[i]]["Graph"]
                #if relabel:
                #    relabels = {}
                #    for node in g.nodes():
                #        h = Crypto.Hash.SHA256.new()
                #        h.update(node)
                #        digest = h.hexdigest()
                #        relabels[node] = digest
                #    nx.relabel_nodes(g, relabels, copy=False)
                newGraph = nx.Graph()
                import code
                code.interact(local=locals())
                for node in g.nodes(data=True):
                    if 'email' in node[1]:
                        node_email = re.search(r'[\w\.-]+@[\w\.-]+',
                                               node[1]['email']).group(0)
                        try:
                            email=data.email_aliases[node_email]
                        except KeyError:
                            email=node_email
                        except:
                            raise
                        h = SHA256.new(crypto_key)
                        h.update(email)
                        email_digest = h.hexdigest()
                        h = SHA256.new(crypto_key)
                        h.update(node[0])
                        name_digest = h.hexdigest()
                        newGraph.add_node(name_digest, email=email_digest)
                for edge in g.edges(data=True):
                    h = SHA256.new(crypto_key)
                    h.update(edge[0])
                    left = h.hexdigest()
                    h = SHA256.new(crypto_key)
                    h.update(edge[1])
                    right = h.hexdigest()
                    newGraph.add_edge(left, right, edge[2])
                nx.write_graphml(newGraph, "/tmp/"+net+str(i)+".xml")
