
#libraries for string comparision
from difflib import SequenceMatcher
import jellyfish as jf
# From address parser
from email.utils import parseaddr

def diffString(string1, string2, algorithm="LE"):
    """by default it uses Levenshtein algorithm, but can be changed
    to Ratcliff-Obershelp. 1 == same string, 0 == no similarity. Thus, I have to
    change the output of Levenshtein"""

    if algorithm == "LE":
        d = jf.levenshtein_distance(string1, string2)
        if d == 0:
            return 1
        else: 
            return float(d)/max(len(string1), len(string2))
    else:
        s = SequenceMatcher(None, string1, string2)
        r = s.ratio()
        return r



def parseAddress(fromField):
    """ returns "name", "user", "domain" from a From: field."""

    # people use brackets in names, not allowed by rfc
    blacklist = "[](){}"
    cleanFrom = ""
    for s in fromField:
        if s not in blacklist:
            cleanFrom += s
    (name, email) = parseaddr(cleanFrom)
    return [name, email.split("@")[0], email.split("@")[1]]


