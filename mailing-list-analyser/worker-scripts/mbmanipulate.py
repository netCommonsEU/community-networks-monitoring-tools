#! /usr/bin/python
import sys
import mailbox
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import getopt 
import re
import time
import email



def purgeAttach(msg, maxSize=0):
    """ a recursive function, inspired by 
    http://code.activestate.com/recipes/252173-extract-kill-mail-attachments/"""

    partsToDelete = []
    index = 0

    payloadList = msg.get_payload()

    #end of recursion
    if type(payloadList) == type(""):
        return

    for part in payloadList:
        maintype =  part.get_content_maintype()
        # remove anything not text, not multipart and larger than
        # maxSize
        if ( maintype != "text" and maintype != "multipart" and
            maintype != "message" and len(part.as_string()) > maxSize):
            print maintype
            print len(part.as_string())
            partsToDelete.append(index)

        if (maintype == "multipart" or maintype == "message"):
            #recursive call
            purgeAttach(part)
        index = index + 1

    listParts = msg.get_payload()
    offset = 0

    for indexToDelete in partsToDelete:
        indexToDelete = indexToDelete - offset
        del listParts[indexToDelete]
        offset += 1

def splitMbox(mbox):
    counter = 1
    if C.getParam("startTime") != C.unset: 
        startDate = time.mktime(
            time.strptime(C.getParam("startTime"), "%d/%m/%Y"))
    else:
        startDate=False
    if C.getParam("endTime") != C.unset: 
        endDate = time.mktime(
            time.strptime(C.getParam("endTime"), "%d/%m/%Y"))
    else:
        endDate=False

    startCounter = C.getParam("start")
    if startCounter == C.unset:
        startCounter = 0
    endCounter = C.getParam("end")
    if endCounter == C.unset:
        endCounter = 0
    mailCounter = -1
    if C.getParam("count") != C.unset:
        mailCounter = 0
    if C.getParam("outmailbox") != C.unset:
        nMbox = mailbox.mbox(C.getParam("outmailbox"))
        nMbox.clear()
    senderDict = set()
    prevMessage = None
    for message in mbox:
        if mailCounter == 0:
            firstDate  = email.utils.parsedate(message["Date"])
        if mailCounter >= 0:
            mailCounter += 1
            senderDict.add(message["From"])
            prevMessage = message
            continue
        if startDate != False:
            date  = time.mktime(email.utils.parsedate(message["Date"]))
        if counter < startCounter or (startDate != False  and 
                date < startDate):
            counter += 1
            continue
        if (endCounter != 0 and counter >= endCounter) or \
            (endDate != False and date > endDate):
            break
        counter += 1
        if C.getParam("purge") != C.unset:
            purgeAttach(message, 4000)
        nMbox.add(message)
    if C.getParam("count") != C.unset:
        lastDate  = email.utils.parsedate(prevMessage["Date"])
        print "The mailbox has", mailCounter, "emails from", len(senderDict),\
           "users"
        print "First message is dated",time.asctime(firstDate)
        print "Last message is dated",time.asctime(lastDate)
    if C.getParam("outmailbox") != C.unset:
        nMbox.flush()
        nMbox.close()

class configuration():
    """ configuration parameters storage class."""

    unset = "UNSETSTRING"
    # the syntax is:
    #  "command line option"->[optionName, wantsValue,.
    #           defaultValue, isSet, usageMessage, type]
    # to add a parameter add a line in the needed/optional row, use
    # getParam("paramName") to get the result or check if it set.

    neededParamsNames = {
            "-f":["inmailbox", True, "", "Input Mailbox file", str]
    }
    #FIXME this must be split in a more generic file and improved
    optionalParamsNames = {
            "-s":["split", False, False, "split mailbox in pieces", bool],
            "-o":["outmailbox", True, "", "Output Mailbox file", str],
            "-c":["count", False, True, "count messages and users", bool],
            "-v":["verbosity", True, 1, "verbosity level 0-2", int],
            "-h":["help", False, False, "show the help", int],
            "-t":["startTime", True, False, 
                    "Start time in the original mailbox: format DD/MM/YYY",
                     str],
            "-T":["endTime", True, False, 
                    "End time in the original mailbox: format DD/MM/YYY",
                     str],
            "-S":["start", True, 0, "Start position in the original mailbox",
                    int],
            "-E":["end", True, 0, "End position in the original mailbox",
                    int],
            "-p":["purge", False, False, "Purge attachments", bool]
            }
    defaultValue = False
    neededParams = {}
    optionalParams = {}

    def __init__(self):
        #for pname, pvalue in self.neededParamsNames.items():
        #    self.neededParams[pvalue[0]] = pvalue[2]
        #for pname, pvalue in self.optionalParamsNames.items():
        #    self.optionalParams[pvalue[0]] = pvalue[2]
        pass

    def checkCorrectnes(self):
        # do some errorchecking here
        if self.getParam("help") != self.unset:
            return False
        if self.getParam("inmailbox") == self.unset:
            print >> sys.stderr
            print >> sys.stderr, "ERROR: Please, specify an input mailbox"
            return False
        if self.getParam("outmailbox") == self.unset and \
            self.getParam("count") == self.unset:
            print >> sys.stderr
            print >> sys.stderr, "ERROR: If you use -s, you have to specify",\
                    "an output mailbox"
            return False
        if (self.getParam("startTime") != self.unset and \
                self.getParam("start") != self.unset)\
            or (self.getParam("endTime") != self.unset and \
                self.getParam("end") != self.unset):
            print >> sys.stderr
            print >> sys.stderr, "ERROR: Can not combine -t/-S -T/-E" 
            return False
        if self.getParam("startTime") != self.unset:
            try:
                time.strptime(self.getParam("startTime"), "%d/%m/%Y")
            except ValueError:
                print >> sys.stderr
                print >> sys.stderr, "ERROR:", self.getParam("startTime"), \
                    "is not a valid start time string, use DD/MM/YYYY"
                return False
        if self.getParam("endTime") != self.unset:
            try:
                time.strptime(self.getParam("endTime"), "%d/%m/%Y")
            except ValueError:
                print >> sys.stderr
                print >> sys.stderr, "ERROR:", self.getParam("endTime"), \
                    "is not a valid end time string, use DD/MM/YYYY"
                return False
        return True

    def printUsage(self):
        print >> sys.stderr
        print >> sys.stderr, "mbmanipulate manipulates mailboxes"
        print >> sys.stderr, "usage",
        print >> sys.stderr, "./mbmanipulate.py: (required parameters)"
        for pname, pvalue in self.neededParamsNames.items():
            print >> sys.stderr, " ", pname, pvalue[3]
        print >> sys.stderr, "(opitional parameters)"
        for pname, pvalue in self.optionalParamsNames.items():
            print >> sys.stderr, " [",pname, pvalue[3], "]"

    def getParam(self, paramName):
        if paramName in self.neededParams.keys():
            return self.neededParams[paramName]
        if paramName in self.optionalParams.keys():
            return self.optionalParams[paramName]
        #unset parameter
        return self.unset

    def printConf(self):
        print ""
        for pname, pvalue in self.neededParams.items():
            print pname, pvalue
        for pname, pvalue in self.optionalParams.items():
            print pname, pvalue


def parseArgs():
     """ argument parser."""

     try:
         #FIXME this should be auto-generated from the parameters list
         opts, args = getopt.getopt(sys.argv[1:], "sS:E:f:pho:t:T:c")
     except getopt.GetoptError, err:
         # print help information and exit:
         print >> sys.stderr,  str(err)
         C.printUsage()
         sys.exit(2)
     for option,v in opts:
         if option in C.neededParamsNames.keys():
             optionValue = C.neededParamsNames[option]
             if optionValue[1] == True:
                 C.neededParams[optionValue[0]] = optionValue[4](v)
             else:
                 C.neededParams[optionValue[0]] = optionValue[2]
         elif option in C.optionalParamsNames.keys():
             optionValue = C.optionalParamsNames[option]
             if optionValue[1] == True:
                 C.optionalParams[optionValue[0]] = optionValue[4](v)
             else:
                 C.optionalParams[optionValue[0]] = optionValue[2]
         else:
             assert False, "unhandled option"
 
     if C.checkCorrectnes() == False:
         C.printUsage()
         sys.exit(1)
     return C



C = configuration()
if __name__ == "__main__":
    """ This cose is just a helper script to parse, split in pieces, 
    remove attachments from mbox files, in order to make them easier to 
    handle. The help from the command line should be self-esplicative"""
    parseArgs()
    mboxFile = C.getParam("inmailbox")
    mbox = mailbox.mbox(mboxFile)
    splitMbox(mbox)
    mbox.close()


