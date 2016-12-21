#!/usr/bin/python
import owner_graph_metrics as ogm
from owner_graph_metrics import dataObject, dd1, dd2, dd3, dd4, dd5
import sys
import getopt
import glob

data = ogm.dataObject()

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:n:d:p:")
    except getopt.GetoptError, err:
        # print help information and exit:
        print >> sys.stderr,  str(err)
        sys.exit(1)
    for option, v in opts:
        if option == "-p":
            try:
                data.initialize(v)
            except IOError:
                print "could not read data file"
                sys.exit(1)
            continue
        if option == "-n":
            data.initialize_names_dictionary(v)
            #ogm.alias_graph_owners(data)
            data.dump_graphs(data)
            continue
        if option == "-d":
            data.dump_db(v, data)
            continue
        if option == "-f":
            file_list = glob.glob(v)
            print file_list
            data.initialize_from_files(file_list)
            continue
    data.dump_graphs(data)

#    try:
#        opts, args = getopt.getopt(sys.argv[1:], "d:f:r:s:pS:vn:k:e:")
#    except getopt.GetoptError, err:
#        # print help information and exit:
#        print >> sys.stderr,  str(err)
#        C.usage()
#        sys.exit(2)
#    for option,v in opts:
#        if option == "-f":
#            C.loadFile = v
#            continue
#        if option == "-d":
#            C.loadDb = "sqlite:///" + v
#            continue
#        if option == "-r":
#            C.numRuns = int(v)
#            continue
#        if option == "-s":
#            C.saveDump = v
#            continue
#        if option == "-p":
#            C.printInfo = True
#            continue
#        if option == "-S":
#            C.createTestRun = True
#            C.saveDump = v
#            continue
#        if option == "-v":
#            C.imageExtension = "eps"
#            continue
#        if option == "-k":
#            C.decryptKey = v
#            continue
#        if option == "-n":
#            C.namesDictionaryFileName = v
#            continue
#        if option == "-e":
#            C.extractDBToFiles = int(v)
#            continue
#    if not C.checkCorrectness():
#        sys.exit(1)
#
#
#    rcParams.update({'font.size': 40})
#    startTime =  datetime.now()
#    print "loading", datetime.now()
#    print C.loadDb
#    if C.loadDb != "":
#        engine = create_engine(C.loadDb)
#        sessionFactory = sessionmaker(bind=engine, autocommit=True)
#        localSession = scoped_session(sessionFactory)
#        C.myCrypto = myCrypto(C.decryptKey)
#        getDataSummary(localSession, data)
#        if C.extractDBToFiles != False:
#            dumpGraphs(data, C.extractDBToFiles, relabel=True)
#            print "Graphs extracted in /tmp folder"
#            sys.exit(0)
#

#
#    loadTime =  datetime.now() - startTime
#    if C.saveDump != "":
#        data.save(C.saveDump)
#        sys.exit()
#
#    logString = ""
#    print "loaded", datetime.now()
#
#    createFolder("CENTRALITY")
#    createFolder("COMPARISON")
#    parsers = []
#    for net in data.rawData:
#        q = Queue()
#        parser = dataParser(net, q)
#        p = Process(target=parser.run, args = (data.rawData[net], 
#    		data.routeData[net], 
#	    	data.dataSummary[net],
#            data.namesDictionary))
#        data.rawData[net] = {}
#        data.routeData[net] = {}
#        data.dataSummary[net] = {}
#        parsers.append((net, p, q))
#        p.start()
#
#    retValues = defaultdict(dict)
#    while True:
#        alive = len(parsers)
#        for (n,p,q) in parsers:
#        	# a process doesn't die if its queue is
#        	# not emptied
#                if not q.empty():
#        	    retValues[n] = q.get()
#        	    print "Subprocess", n, "exited"
#        	if not p.is_alive():
#        	    alive -= 1
#        	
#        if alive == 0:
#            break
#        time.sleep(1)
#    extractDataSeries(retValues)
#
#    f = open(C.resultDir+"/logfile.txt", "w")
#    runTime = datetime.now() - startTime - loadTime
#    print >> f,  data.printSummary()
#    print >> f, logString
#    print >> f, "Whiskers = q3+/-1.5*IQR"
#    print >> f, "loadTime =", loadTime, "runTime =", runTime
#    f.close()


