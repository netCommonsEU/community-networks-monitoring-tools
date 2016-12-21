from collections import defaultdict, Counter
import cPickle as pk
import simplejson
import re
import networkx as nx
from Crypto.Hash import SHA256
import datetime

try:
    import key
    crypto_key = key.crypto_key
except:
    ImportError
    print "You don't have a crypo key file included, using default one"
    crypto_key = "12345"
    pass

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
except:
    ImportError
    print "You do not seem to have sqlalchemy installed, you will"
    print "not be able to use SQL functions"
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

#################################


class dataObject:
    """ This class is used to store and manipulate datasets """

    def __init__(self):
        """ Initialize the data object. The dd* structs are needed
        if you want to save the data in a pickle format, that is
        faster to read/save """

        self.scanTree = dd2()
        self.dataSummary = dd3()
        self.dumpFile = ""
        self.routeData = dd5()
        self.etxThreshold = -1
        self.namesDictionary = {}
        self.email_aliases = {}

    def initialize(self, fileName):
        """ read from a pickle file """

        self.dumpFile = fileName
        try:
            f = open(self.dumpFile, "r")
        except IOError:
            print "could not load", self.dumpFile
            raise
        d = pk.load(f)
        self.scanTree = d.scanTree
        self.dataSummary = d.dataSummary
        self.routeData = d.routeData
        f.close()

    def save(self, fileName):
        """ save data in a pickle file """

        f = open(fileName, "w")
        pk.dump(self, f)
        f.close()

    def initialize_from_files(self, file_list):
        """ initialize from a list of graphml files. Each graphml should
        contain an "email" field per node that identifies the owner and
        a scan_id, scan_time and network global field to identify the scan
        and network """

        for file in file_list:
            try:
                g = nx.read_graphml(file)
            except:
                raise
            self.scanTree[g.graph["network"]]["ETX"].append(
                    [g.graph["scan_id"], g.graph["scan_time"]])
            self.routeData[g.graph["network"]][g.graph["scan_id"]]["Graph"] = g

    def get_owner_distribution(self, graph, silent=True):
        """ plot a distribution of ownership of the nodes """

        # two helper structures
        nodeOwner = {}  # node -> owner
        ownerNodes = defaultdict(list)  # owner -> [nodes]
        for n in graph.nodes(data=True):
            nodeOwner[n[0]] = n[1]["email"]
            ownerNodes[n[1]["email"]].append(n[0])

        if not silent:
            print "# owner".rjust(long_align_space), ",",\
                  "owned nodes".rjust(long_align_space)
            for owner, nodes in sorted(ownerNodes.items(),
                                       key=lambda(x): -len(x[1])):
                print owner.rjust(30), ",",  str(len(nodes)).rjust(30)
            print ""
            print ""
        return ownerNodes, nodeOwner

    def computePrefAttachTrend(self, net):
        """ Given a seuqence of timestamped network graphs, compute the
        cumulative probability of new nodes of attaching to existent
        nodes in function of their degree """

        nodeDict = {}
        linkSet = defaultdict(dict)
        nodeCounter = Counter()
        sizeArray = []
        occurrencies = defaultdict(Counter)
        year_map = defaultdict(list)
        for scan_id in self.routeData[net]:
            g = self.routeData[net][scan_id]["Graph"]
            y = datetime.datetime.strptime(g.graph["scan_time"],
                                           "%Y-%m-%d %H:%M:%S.%f").year
            year_map[y].append(g.graph["scan_id"])
        for y in sorted(year_map.keys()):
            firstRun = True
            for scanId in year_map[y]:
                G = self.routeData[net][scanId]["Graph"]
                if max(nx.degree(G).values()) > 32:
                    #  FFWien has some inexplicable peaks in which the network
                    #  shows about 320 nodes with some that have more than 40
                    #  neighbors
                    continue

                for node in G.nodes():
                    if node not in nodeDict:
                        nodeDict[node] = scanId
                        nodeCounter[scanId] += 1
                        if not firstRun:
                            neighs = G.neighbors(node)
                            for nei in neighs:
                                deg = G.degree(nei)
                                if deg != 1:
                                    occurrencies[y][deg-1] += 1
                sizeArray.append(len(G))
                for l in G.edges():
                    if l not in linkSet:
                        deg = max(G.degree(l[0]), G.degree(l[1]))
                        linkSet[l][scanId] = deg
                if firstRun:
                    firstRun = False
            numEntries = 1.0*sum(x[1] for x in occurrencies[y].items())
            for x in occurrencies[y]:
                occurrencies[y][x] = occurrencies[y][x]/numEntries
        maxDeg = max([occurrencies[x].keys()[-1] for x in
                     occurrencies if len(occurrencies[x])])
        print "degree",
        for year in sorted(occurrencies.keys()):
            print year,
        print

        for j in range(1, maxDeg+1):
            print j,
            for year in sorted(occurrencies.keys()):
                if j in occurrencies[year]:
                    print occurrencies[year][j],
                else:
                    print 0,
            print ""

        print ""
        print ""
        print "degree",
        for year in sorted(occurrencies.keys()):
            print year,
        print
        for j in range(1, maxDeg+1):
            print j,
            for year in sorted(occurrencies.keys()):
                print sum(occurrencies[year].values()[0:j]),
            print ""

    def getOwnerCentrality(self, graph):
        """ compute the network centrality of all the nodes owned by a person
        with respect to all shortest paths beteween nodes"""

        personCent = defaultdict(int)
        ownerNodes, nodeOwner = self.get_owner_distribution(graph)
        allp = nx.all_pairs_shortest_path(graph)
        counter = 0
        for s in allp:
            for d in allp[s]:
                counter += 1
                matched_people = []
                for node in allp[s][d]:
                    if nodeOwner[node] not in matched_people:
                        personCent[nodeOwner[node]] += 1
                        matched_people.append(nodeOwner[node])
        print "# owner".rjust(long_align_space), ",",\
              "owner centrality".rjust(long_align_space)
        for (p, c) in sorted(personCent.items(), key=lambda x: -x[1]):
            print p.rjust(long_align_space), ",",\
                str(c*1.0/counter).rjust(long_align_space)
        print ""
        print ""

        return personCent, counter

    def getOwnerToOwnerCentrality(self, graph):
        """ compute the network centrality of all the nodes owned by a person
        with respect to all shortest paths beteween any owner"""

        nodeOwner = {}  # node -> owner
        ownerNodes = defaultdict(list)  # owner -> [nodes]
        ownerCentrality = defaultdict(int)
        ownerNodes, nodeOwner = self.get_owner_distribution(graph)
        counter = 0
        shortestPathAndDistance = {}
        for n in graph.nodes():
            shortestPathAndDistance[n] = nx.single_source_dijkstra(graph, n)
            # returns a couple (distance, path)
        for i in range(len(ownerNodes)):
            from_owner, from_nodes = ownerNodes.items()[i]
            for j in range(i+1, len(ownerNodes)):
                to_owner, to_nodes = ownerNodes.items()[j]
                shortest_path = []
                shortest_cost = 0
                for s in from_nodes:
                    for d in to_nodes:
                        if not shortest_path or shortestPathAndDistance[s][0][d] < shortest_cost:
                                shortest_path = shortestPathAndDistance[s][1][d]
                                shortest_cost = shortestPathAndDistance[s][0][d]
                counter += 1
                path_set = set([nodeOwner[node] for node in shortest_path])
                for o in path_set:
                    ownerCentrality[o] += 1
        print "# owner".rjust(long_align_space), ",",\
              "owner-to-owner cent.".rjust(long_align_space)
        for (p, c) in sorted(ownerCentrality.items(), key=lambda x: -x[1]):
            print p.rjust(long_align_space), ",",\
                str(c*1.0/counter).rjust(long_align_space)
        print ""
        print ""
        return ownerCentrality, counter

    def getOwnerRobustness(self, graph):
        """ compute the "owner robustness """

        ownerNodes, nodeOwner = self.get_owner_distribution(graph)
        print "# owner".rjust(long_align_space), ",",\
              "main C. size".rjust(long_align_space), ",",\
              "number of components".rjust(long_align_space)
        for owner, nodes in sorted(ownerNodes.items(),
                                   key=lambda(x): -len(x[1])):
            purged_graph = nx.Graph(graph)
            for n in nodes:
                purged_graph.remove_node(n)
            comp_list = list(nx.connected_components(purged_graph))
            main_comp = sorted(comp_list, key=len, reverse=True)[0]
            print owner.rjust(long_align_space), ",",\
                str(len(main_comp)).rjust(long_align_space), ",", \
                str(len(comp_list)).rjust(long_align_space)
        print ""
        print ""

    #  ################# helper functions
    # These functions are needed to handle data structures from
    # other sources of data. You can use a database and dump the
    # data in XML from a db. You probably do not need these functions.

    def initialize_names_dictionary(self, file_name):
        """ the alias dictionary is a dictionary that mathces multiple
        "From" email fields to one person. It is derived from "From" fields
        taken from parsing a mailing list mbox. It is in the form:
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
        for e in self.namesDictionary.items():
            # merge aliases into unique names
            alias_email = re.search(r'[\w\.-]+@[\w\.-]+',
                                    e[0]).group(0)
            unique_email = e[1][2][1] + "@" + e[1][2][2]
            self.email_aliases[alias_email] = unique_email

    def printSummary(self):
        """ just dump a summary of the dataset """

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
                for k, value in self.dataSummary[net][sid].items():
                    logString += str(value).ljust(k[1]) + " "
                logString += "\n"
        logString += "\n\nETX threshold:" + str(self.etxThreshold)

        return logString

    def dump_graphs(self, data, graphNumber=0):
        """ this function dumps in the /tmp/ folder a number of graphs in
        graphml format. import a key.py file with the definition of a
        key="123" variable used to initialize the hashes """

        for net in data.routeData:
            scanIdList = data.routeData[net].keys()
            for i in range(len(scanIdList)):
                if not graphNumber or i < graphNumber:
                    g = data.routeData[net][scanIdList[i]]["Graph"]
                    newGraph = nx.Graph()
                    # copy the graph metaattributes
                    newGraph.graph = g.graph
                    for node in g.nodes(data=True):
                        if 'email' in node[1]:
                            try:
                                node_email = re.search(r'[\w\.-]+@[\w\.-]+',
                                                     node[1]['email']).group(0)
                            except AttributeError:
                                node_email = ""
                            try:
                                email = data.email_aliases[node_email]
                            except KeyError:
                                email = node_email
                            except:
                                raise
                            h = SHA256.new(crypto_key)
                            h.update(email)
                            email_digest = h.hexdigest()
                        else:
                            email_digest = ""
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
                    print newGraph.graph, g.graph
                    nx.write_graphml(newGraph, "/tmp/"+net+str(i)+".xml")

    def dump_db(self, db_file, data):
        """ dump the graphs from a database. This is for legacy
        compatibility with the communityNetworkMonitor project """

        engine = create_engine("sqlite:///" + db_file)
        sessionFactory = sessionmaker(bind=engine, autocommit=True)
        localSession = scoped_session(sessionFactory)
        self.getOldDataSummary(localSession, data)
        self.dump_graphs(data)

    def getOldDataSummary(self, ls, data):
        """ dump the graphs from a database. This is for legacy
        compatibility with the communityNetworkMonitor project """

        scanQuery = "SELECT * from scan"
        QUERY = """select snode.Id AS sid, dnode.Id AS did, etx.etx_value AS etxv from \
               link, scan, node as snode, node as dnode, etx \
               WHERE link.scan_Id = scan.Id AND snode.Id = link.from_node_Id \
               AND dnode.Id = link.to_node_Id AND etx.link_Id = link.Id \
               AND dnode.scan_Id = scan.Id AND snode.scan_Id = scan.Id AND \
               scan.Id= %d"""

        try:
            q = ls.query("Id", "time", "scan_type", "network").from_statement(
                    scanQuery)
            if len(q.all()) == 0:
                raise
        except:
            print "something went wrong opening the db"
            import sys
            sys.exit(1)

        numScan = len(q.all())
        scanCounter = 0
        data.etxThreshold = 10
        for [scanId, scanTime, scanType, scanNetwork] in q:
            data.scanTree[scanNetwork][scanType].append([scanId, scanTime])

        for net in data.scanTree:
            counter = 0
            # for graz I have one sample every 10 minutes,
            # for ninux/Wien I have one sample every 5 minutes
            if net == "FFGraz":
                networkPenalty = 2
            else:
                networkPenalty = 1
            for scanId in data.scanTree[net]['ETX']:
                queryString = QUERY % scanId[0]
                q = ls.query("sid", "did", "etxv").\
                    from_statement(queryString)
                dirtyG = nx.Graph()
                for s, d, e in q:
                    if e < data.etxThreshold:
                        dirtyG.add_edge(s, d, weight=float(e))

                if len(dirtyG) != 0:
                    G = max(nx.connected_component_subgraphs(dirtyG,
                            copy=True), key=len)
                    componentSize = len(G)
                    G.graph = {"network": net, "scan_time": scanId[1],
                               "scan_id": scanId[0]}
                else:
                    G = nx.Graph()
                    componentSize = 0
                if componentSize < 10:
                    continue
                counter += 1

                etxV = [e[2]['weight'] for e in G.edges(data=True)]
                data.routeData[net][scanId[0]]["Graph"] = G
                weightedPaths = nx.shortest_path(G, weight="weight")
                for s in G.nodes():
                    for d in G.nodes():
                        if s == d:
                            continue
                        if d in data.routeData[net][scanId[0]]["data"] and \
                                s in data.routeData[net][scanId[0]]["data"][d]:
                            continue
                        currPath = weightedPaths[s][d]
                        pathWeight = 0
                        for i in range(len(currPath) - 1):
                            pathWeight += G[currPath[i]][currPath[i+1]]["weight"]
                        data.routeData[net][scanId[0]]["data"][s][d] = \
                                      [len(weightedPaths[s][d])-1, pathWeight]
                data.routeData[net][scanId[0]]["Graph"] = G
                nd = filter(lambda x: x == 1, dirtyG.degree().values())
                nl = len(nd)
                nn = len(dirtyG)
                le = len(etxV)
                data.dataSummary[net][scanId[0]][("numLeaves", 9)] = nl
                data.dataSummary[net][scanId[0]][("time", 30)] = scanId[1]
                data.dataSummary[net][scanId[0]][("numNodes", 9)] = nn
                data.dataSummary[net][scanId[0]][("numEdges", 9)] = le
                data.dataSummary[net][scanId[0]][("largestComponent", 16)] = \
                    componentSize
                scanCounter += 1
                if int((100000 * 1.0*scanCounter / numScan)) % 10000 == 0:
                    print int((100 * 1.0*scanCounter / numScan)), "% complete"
