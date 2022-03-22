import time
import string

def SortBy(sequence, n, bReversed=0, cmpfunc=None):
    """
    Function to sort a list of lists/tuples according to the n-th field of each list/tuple
    --see: http://musi-cal.mojam.com/~skip/python/fastpython.html#sorting

    Parameters
    ----------
    sequence :
    n :
    bReversed :
    cmpfunc :

    Returns
    -------

    """

    nlist = list(map(lambda x, n=n: (x[n], x), sequence))
    if cmpfunc is None: nlist.sort()
    else: nlist.sort(cmpfunc)
    l = [key_x[1] for key_x in nlist]
    if bReversed: l.reverse() #according to Python docs it is faster to reverse list than specify a special compare function to sort()
    return l

def GetCurrentTimeStr():
    currTimeSSE=time.time()
    cyear,cmonth,cmonthday,chour,cmin,csec,cwkday,cdoy,cdlsf = time.localtime(currTimeSSE)
    currTimeCarisStr=str(cyear)+'-%03d.'%cdoy+'%02d:%02d:%02d'%(chour,cmin,csec)
    return currTimeCarisStr+' ('+"%.0f"%currTimeSSE+')'

def SortBy2(sequence, n, m, nReversed=0, mReversed=0, nIsNumber=0, mIsNumber=0):
# Function to sort a list of lists/tuples by n-th field, then by m-th field of each list/tuple
# --adapted from Python Cookbook recipe 2.4
    if n==m:
        return SortBy(sequence, n, nReversed)
    # Pack a better-ordered auxiliary list, suitable for .sort()
    if not (nReversed or mReversed):
        nmlist = list(map(lambda x, n=n,m=m: (x[n], x[m], x), sequence))
    else:
        if nReversed: nMult=-1
        else: nMult=1
        if mReversed: mMult=-1
        else: mMult=1
        if nIsNumber and mIsNumber: # n-th & m-th fields are numbers
            nmlist = list(map(lambda x, n=n,m=m: (nMult*x[n], mMult*x[m], x), sequence))
        else:    
            all_chars = string.maketrans('','')
            all_charsL = list(all_chars)
            all_charsL.reverse()
            rev_chars = ''.join(all_charsL)
            rev_trans = string.maketrans(all_chars, rev_chars)
            if nIsNumber: # and m-th field is string
                if mReversed:
                    nmlist = list(map(lambda x, n=n,m=m: (nMult*x[n],
                                                     string.translate(x[m], rev_trans),
                                                     x),
                                 sequence))
                else:
                    nmlist = list(map(lambda x, n=n,m=m: (nMult*x[n], x[m], x), sequence))
            elif mIsNumber: # and n-th field is string
                if nReversed:
                    nmlist = list(map(lambda x, n=n,m=m: (string.translate(x[n], rev_trans),
                                                     mMult*x[m],
                                                     x),
                                 sequence))
                else:
                    nmlist = list(map(lambda x, n=n,m=m: (x[n], mMult*x[m], x), sequence))
            else: # n-th & m-th fields are strings
                if not (nReversed or mReversed):
                    nmlist = list(map(lambda x, n=n,m=m: (x[n], x[m], x), sequence))
                elif nReversed:
                    nmlist = list(map(lambda x, n=n,m=m: (string.translate(x[n], rev_trans),
                                                     x[m],
                                                     x),
                                 sequence))
                elif mReversed:
                    nmlist = list(map(lambda x, n=n,m=m: (x[n],
                                                     string.translate(x[m], rev_trans),
                                                     x),
                                 sequence))
                else:
                    nmlist = list(map(lambda x, n=n,m=m: (string.translate(x[n], rev_trans),
                                                     string.translate(x[m], rev_trans),
                                                     x),
                                 sequence))
    nmlist.sort()    # Sort in a simple & fast way
    return [x[-1] for x in nmlist]    # Unpack the sorted sequence

# Adapted from Python Cookbook (receipe 2.1 Sorting a Dictionary, by Martelli & Hettinger)
def GetSortedDictItems(adict):
    items = sorted(list(adict.items()))
    return [(key,value) for key,value in items]

# Python Cookbook receipe 157358
# Title: Lightweight XML constructor and reader 
# Submitter: Dirk Holtwick
# Last Updated: 2002/10/18 
# Version no: 1.0 
# Category: XML 
from xml.dom.minidom import Document, parse, parseString
import string

defaultencoding = "utf-8"

def _encode(v):
    #if isinstance(v, UnicodeType):
    #    v = v.encode(defaultencoding)
    return v

class XMLElement:

    def __init__(self, doc, el):
        self.doc = doc
        self.el = el

    def __getitem__(self, name):
        a = self.el.getAttributeNode(name)
        if a:
            return _encode(a.value)
        return None

    def __setitem__(self, name, value):
        self.el.setAttribute(name, _encode(value))

    def __delitem__(self, name):
        self.el.removeAttribute(name)

    def __str__(self):
        return _encode(self.doc.toprettyxml())

    def toString(self):
        return _encode(self.doc.toxml())

    def _inst(self, el):
        return XMLElement(self.doc, el)

    def get(self, name, default=None):
        a = self.el.getAttributeNode(name)
        if a:
            return _encode(a.value)
        return _encode(default)

    def add(self, tag, **kwargs):
        el = self.doc.createElement(tag)
        for k, v in list(kwargs.items()):
            el.setAttribute(k, _encode(str(v)))
        return self._inst(self.el.appendChild(el))

    def addText(self, data):
        return self._inst(
            self.el.appendChild(
                self.doc.createTextNode(_encode(data))))

    def addComment(self, data):
        return self._inst(
            self.el.appendChild(
                self.doc.createComment(data)))

    def getText(self, sep=" "):
        rc = []
        for node in self.el.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return _encode(string.join(rc, sep))

    def getAll(self, tag):
        return list(map(self._inst, self.el.getElementsByTagName(tag)))

class _Document(Document):

    def writexml(self, writer, indent="", addindent="", newl=""):
        writer.write('<?xml version="1.0" encoding="%s" ?>\n' % defaultencoding)
        for node in self.childNodes:
            node.writexml(writer, indent, addindent, newl)
# @todo check that XMLDocument works in Python 3 since it uses _encode function above which was based on Python2
class XMLDocument(XMLElement):

    def __init__(self, tag=None, **kwargs):
        self.doc  = _Document()
        XMLElement.__init__(self, self.doc, self.doc)
        if tag:
            self.el = self.add(tag, **kwargs).el

    def parse(self, d):
        self.doc = self.el = parse(d)
        return self

    def parseString(self, d):
        self.doc = self.el = parseString(_encode(d))
        return self

if __name__=="__main__":

    # Example of dumping a database structure
    doc = XMLDocument("database", name="testdb")
    table = doc.add("table", name="test")
    table.add("field", name="counter", type="int")
    table.add("field", name="name", type="varchar")
    table.add("field", name="info", type="text")
    print(doc)

    # Simulate reading a XML file
    ndoc = XMLDocument()
    ndoc.parseString(str(doc))
    root = ndoc.getAll("database")
    if root:
        db = root[0]
        print("Database:", db["name"])
        for table in db.getAll("table"):
            print("  Table:", table["name"])
            for field in db.getAll("field"):
                print("    Field:", field["name"], "- Type:", field["type"])

    # It's object oriented
    print(XMLDocument("notice").add("text",format="plain").addText("Some text"))

# The following time routines are based on those developed by Dr. Ben W. Remondi
def ydhms_mjd(year, yday, hour, minute, second):
    days_per_second = 0.00001157407407407407
    mjd_tojan11901 = 15385
    years_into_election = (year-1)%4
    elections = (year-1901)/4
    fmjd = (hour*3600 + minute*60 + second)*days_per_second
    mjd = mjd_tojan11901 + elections*1461 + years_into_election*365 + yday - 1
    return (mjd, fmjd)
def mjd_gps(mjd, fmjd):
    mjd_tojan61980 = 44244
    idays = mjd - mjd_tojan61980
    gpswk = idays/7
    dayofwk = idays - gpswk*7
    secofwk = (dayofwk + fmjd)*86400
    return (gpswk,secofwk)
def ydhms_gps(year, yday, hour, minute, second):
    mjday,fmjd = ydhms_mjd(year,yday,hour,minute,second)
    gpswk,secofwk = mjd_gps(mjday,fmjd)
    return (gpswk,secofwk)

import os.path, fnmatch
# Function to return a list of all the files, and optionally folders, that match a certain pattern in a directory [tree]
# --Python Cookbook recipe 4.18
def listFiles(root, patterns='*', recurse=1, return_folders=0):
    # Expand patterns from semicolon-separated string to list
    pattern_list = patterns.split(';')
    # Collect input and output arguments into one bunch
    class Bunch:
        def __init__(self, **kwds): self.__dict__.update(kwds)
    arg = Bunch(recurse=recurse, pattern_list=pattern_list, return_folders=return_folders, results=[])
    
    def visit(arg, dirname, files):
        # Append to arg.results all relevant files (and perhaps folders)
        for name in files:
            fullname = os.path.normpath(os.path.join(dirname, name))
            if arg.return_folders or os.path.isfile(fullname):
                for pattern in arg.pattern_list:
                    if fnmatch.fnmatch(name, pattern):
                        arg.results.append(fullname)
                        break
        # Block recursion if recursion was disallowed
        if not arg.recurse: files[:]=[]
    os.path.walk(root, visit, arg)
    return arg.results

# http://mail.python.org/pipermail/python-list/2003-May/202712.html
def binstr(n, maxbits=None):
    absn = abs(n)
    s=[chr(((n>>b)&1)+48) for b in range(maxbits or len(hex(n))*4) if maxbits or not b or absn>>(b-1)]
    s.reverse()
    return ''.join(s)