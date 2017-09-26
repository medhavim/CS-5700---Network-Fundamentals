import sys
import urllib2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import os
from sys import getsizeof
from SocketServer import ThreadingMixIn
from collections import OrderedDict
import zlib
from collections import Mapping, Container
import thread
import threading
import getopt

# To maintain files in memory cache
mCache = OrderedDict()
# To maintain files in disk cache
dCache = []

# Set maximum cache size to 10MB
MAX_DISK_SPACE = 10000000
MAX_MEM_SPACE =  10000000
#MAX_MEM_SPACE =  1000

##############################################################
# The Class that deals with the cache management 
##############################################################
class localCache():
    global mCache
    global dCache
    global oHost
    global oPort

    def __init__(self):
        self.filename = ''

    #################################################
    # Function: getMemoryFile
    # Input: The name of the file
    # Output: The content of the file
    # Description: This function decompresses the file 
    #    present in the memory cache and returns the 
    #    contents of the file
    ################################################# 
    def getMemoryFile(self, filename):
	c = mCache[filename]
        content = zlib.decompress(c)
        mCache.pop(filename)
        mCache[filename] = c
	return content

    #################################################
    # Function: getDiskFile
    # Input: The name of the file
    # Output: The content of the file
    # Description: This function decompresses the file 
    #    present on the disk cache and returns the  
    #    contents of the file
    #################################################
    def getDiskFile(self, filename):
        fname = open('cache/'+filename,'r')
        content = zlib.decompress(fname.read())
        dCache.remove(filename)		
        dCache.append(filename)
        return content
##############################################################
# My Custome HTTP Handler to handle the incoming requests 
##############################################################
class customHTTPHandler(BaseHTTPRequestHandler):
    global mCache
    global dCache
    global oHost
    global oPort

    cch = localCache()
    def do_GET(self):
        filename = self.path[1:]
        filename = filename.replace("/","_")
        getRequest = 'http://'+oHost+':'+str(oPort)+self.path
        try:
	    # Check if the file is already present in the memory cache
            if filename in mCache:
	        content = self.cch.getMemoryFile(filename)
                self.writeData(content)
                return

            # If file is not found in memory, chck if the file is present in the disk Cache
            elif filename in dCache:
		content = self.cch.getDiskFile(filename)
                self.writeData(content)
                return
	    # If file is not present in either the Memory of the Disk Cache,
	    # Request from origin
            else:
                try:
                    data = urllib2.urlopen(getRequest).read()

                except urllib2.HTTPError as e1:
                    self.send_error(e1.code, e1.reason)
                    return
                except urllib2.URLError as e2:
                    self.send_error(e2.reason)
                    return

                try:
                    while (getContentSize(mCache, set()) + getContentSize(zlib.compress(data),set()))  >= MAX_MEM_SPACE:
                        if len(mCache) != 0:
                            poppedItem = mCache.popitem(last=False)
                            diskSpace = getDiskSpace(".")
                            contentSize = getContentSize(poppedItem[1],set())

			    # If both memory and disk are full, delete the least recently used file
                            while (diskSpace + contentSize) > MAX_DISK_SPACE:
                                if len(dCache) != 0:
                                    fileToBeDeleted = dCache.pop(0)
                                    os.remove('cache/'+fileToBeDeleted)
                                    diskSpace = getDiskSpace("cache")
                                else:
                                    self.writeData(data)
                                    return
                            f = open('cache/'+poppedItem[0],'w')
                            f.write(poppedItem[1])
                            f.close()
                            dCache.append(poppedItem[0])
                        else:
                            self.writeData(data)
                            return
                    mCache[filename] = zlib.compress(data)
                    self.writeData(data)
                    return
                except Exception,e:
            	    #print (" An error has occured. So will try to forward request to Origin Server")
                    self.writeData(data)

        except Exception,e:
            #print (" An error has occured. So will try to forward request to Origin Server")
	    #print(e)
            try:
                oData = urllib2.urlopen(getRequest).read()
                self.writeData(oData)
            except urllib2.HTTPError, e:
                self.send_response(e.code)
                self.send_header('Content-type','text/html')
                self.end_headers()
                return
##############################################################
# The function that downloads the requested data 
##############################################################
    def writeData(self, message):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(message)
	#print "Mem-Cache size="+str(getContentSize(mCache, set()))
        #print "Disk-Cache size="+str(getDiskSpace("."))
##############################################################
# The Class makes parallel requests 
##############################################################
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """New thread for parallel requests"""

##############################################################
# Function: getDiskSpace 
# Input: the path of the directory 
# Output: Returns the size of the input directory 
# Description: This function returns the size of the given directory 
##############################################################
def getDiskSpace(path):
    path = "."
    dirSize = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for fname in filenames:
            fp = os.path.join(dirpath, fname)
            dirSize += os.path.getsize(fp)
    return dirSize


##############################################################
# Function: getContentSize 
# Input: The object whose size is to be known 
# Output: Returns the size of the input object 
# Description: This function checks the size of the input object 
##############################################################
def getContentSize(obj, s):
    contentSize = getContentSize
    if id(obj) in s:
        return 0
    size = getsizeof(obj)
    s.add(id(obj))
    if isinstance(0, unicode) or isinstance(obj, str):
        return size
    if isinstance(obj, Mapping):
	size = size + sum(contentSize(key, s) + contentSize(val, s) for key, val in obj.iteritems())
        return size 
    if isinstance(obj, Container):
	size = size + sum(contentSize(tup, s) for tup in obj)
        return size
    return size

##############################################################
# Function: parse 
# Input: the arguements provided to the file
# Output: The port and the origin on which this file should run
##############################################################
def parse(argvs):
    (port, origin) = (0, '')
    opts, args = getopt.getopt(argvs[1:], 'p:o:')
    for o, a in opts:
        if o == '-p':
            port = int(a)
        elif o == '-o':
            origin = a
        else:
            sys.exit('USAGE: ./httpserver -p <port> -o <origin>')
    return port, origin

##############################################################
# The main function of the program that listens for incoming requests
##############################################################
def main():
    global oHost
    global oPort
    global MAX_DISK_SPACE

    httpServerPort, oHost = parse(sys.argv) 
    oPort = 8080

    # Create the Cache folder
    os.system("mkdir -p cache")
    #Clearing cache folder before starting
    os.system("rm -f cache/*")
    MAX_DISK_SPACE = 10000000 - getDiskSpace(".")
    httpServer = ThreadedHTTPServer(('',httpServerPort),customHTTPHandler)
    s = httpServer.socket.getsockname()
    #print "Serving HTTP on", s[0], "port", s[1], "..."
    try:
        httpServer.serve_forever()
    except:
        print( "Exception")
    finally:
        print ("Graceful Exit")
        httpServer.socket.close()

if __name__ == '__main__':
	main()
