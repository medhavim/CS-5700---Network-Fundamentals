import sys
import urllib2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import os
import zlib
from collections import Mapping, Container
from sys import getsizeof
from collections import OrderedDict
from SocketServer import ThreadingMixIn



mCache = OrderedDict()
dCache = []

# Gets the size of the a given Directory
def getDiskSpace(path):
    path = "."
    dirSize = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            dirSize += os.path.getsize(fp)

    print "DirSize ="   + str(dirSize)
    return dirSize

#Set cache size
MAX_DISK_SPACE = 10000000
MAX_MEM_SPACE =  10000000

print 'MAX_DISK_SPACE = '+ str(MAX_DISK_SPACE)
httpServer = ''
oPort = 8080
#oHost = 'ec2-54-167-4-20.compute-1.amazonaws.com'
oHost = 'localhost'


def main():


    global oHost
    global oPort
    global MAX_DISK_SPACE

    if len(sys.argv) < 5:
        print "Please run with the following arguments -  ./httpserver -p <port> -o <origin>"
        #   sys.exit(0)
    httpServerPort = int(sys.argv[2])
    oHost = sys.argv[4]

    oPort = 8080

    #oHost = 'localhost'
    #oHost = 'ec2-54-88-98-7.compute-1.amazonaws.com'
    #Clearing cache folder before starting
    os.system("rm -f cache/*")
    MAX_DISK_SPACE = 10000000 - getDiskSpace(".")

    httpServer = ThreadedHTTPServer(('',httpServerPort),myHandlerClass)
    s = httpServer.socket.getsockname()
    print "Serving HTTP on", s[0], "port", s[1], "..."
    try:
        print 'OriginServer=' + oHost
        httpServer.serve_forever()
    except:
        print "Exception"

    finally:
        print 'Exiting Gracefully'
        httpServer.socket.close()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handling parallel requests"""

class cache():
    global mCache
    global dCache
    global oHost
    global oPort

    def getMemoryFile(filename):
	c = mCache[filename]
        retrievedContent = zlib.decompress(c)
        mCache.pop(filename)
        mCache[filename] = c
	return retrievedContent

    def getDiskFile(filename):
	print "fetching from disk"
        fname = open('cache/'+filename,'r')
        retrievedContent = zlib.decompress(fname.read())
        # Updating cache to keep track of most recently seen
        dCache.remove(filename)
        dCache.append(filename)
        return retrievedContent

class myHandlerClass(BaseHTTPRequestHandler):
    global mCache
    global dCache
    global oHost
    global oPort


    def do_GET(self):

        #resource to GET
        #rs = self.path


        filename = self.path[1:]
        filename = filename.replace("/","_")


        #Frame GET request
        getRequest = 'http://'+oHost+':'+str(oPort)+self.path
        print 'GET REQUEST=' + getRequest
        try:


        #Check filename in in memory cache

            if filename in mCache:

                #print "Returning from in mem cache"
                # Updating cache to keep track of most recently seen
                #c = mCache[filename]
                #retrievedContent = zlib.decompress(c)
                #mCache.pop(filename)
                #mCache[filename] = c

                # print "Mem-Cache size="+str(getContentSize(mCache, set()))
	        retrievedContent = cache.getMemoryFile(filename)
                self.returnToClient(retrievedContent)

                return

            #if not found in mem, check dCache
            elif filename in dCache:
		retrievedContent = cache.getDiskFile(filename)
                #print "fetching from disk"
                #fname = open('cache/'+filename,'r')
                #retrievedContent = zlib.decompress(fname.read())
                # Updating cache to keep track of most recently seen
                #dCache.remove(filename)
                #dCache.append(filename)

                self.returnToClient(retrievedContent)
                return


            #if file not found in disk cache, make request to origin
            else:
                print "from origin"

                try:
                    downloadedContent = urllib2.urlopen(getRequest).read()

                except urllib2.HTTPError as e1:
                    self.send_error(e1.code, e1.reason)
                    return
                except urllib2.URLError as e2:
                    self.send_error(e2.reason)
                    return



                # Retreive from Origin server
                try:
                    print str(getContentSize(zlib.compress(downloadedContent),set()))+ "," +\
                          str(getContentSize(mCache, set()) + getContentSize(zlib.compress(downloadedContent),set())) + "," +\
                          str(MAX_MEM_SPACE)
                    #If no space in mem cache, spill over to disk cache
                    while (getContentSize(mCache, set()) + getContentSize(zlib.compress(downloadedContent),set()))  >= MAX_MEM_SPACE:

                        print "In mem Cache Limit exceeded, spilling over to disk"

                        if len(mCache) != 0:
                            poppedItemFromMem = mCache.popitem(last=False)


                            diskSpace = getDiskSpace(".")
                            cs = getContentSize(poppedItemFromMem[1],set())
                            print "diskspace= " + str(diskSpace) + " spilled over cs is " + str(getContentSize(poppedItemFromMem,set())) + "cs is " + str(cs) + " max=" + str(MAX_DISK_SPACE)
                            #If disk cache is also full, start deleting content from cache
                            while (diskSpace + cs) > MAX_DISK_SPACE:

                                if len(dCache) != 0:
                                    fileToBeDeleted = dCache.pop(0)
                                    print "file deleted to make space"
                                    os.remove('cache/'+fileToBeDeleted)
                                    diskSpace = getDiskSpace("cache")
                                else:
                                    print "File doesnt fit in Disk . Hence cant cache this"
                                    self.returnToClient(downloadedContent)
                                    return


                            f = open('cache/'+poppedItemFromMem[0],'w')

                            f.write(poppedItemFromMem[1])
                            f.close()
                            dCache.append(poppedItemFromMem[0])

                        else:
                            #If file is too big for both disk and mem cach, send to client without caching
                            print "File too big to be cached"
                            self.returnToClient(downloadedContent)
                            return


                    # Now MEM has enough space. SO push into Mem
                    print "Writing to in-mem"
                    mCache[filename] = zlib.compress(downloadedContent)


                    self.returnToClient(downloadedContent)
                    return

                except Exception,e:
                    # Handling Caching Error
                    # Error in caching. Send to client right away
                    print "Error in caching. Send to client right away :" + e.message
                    self.returnToClient(downloadedContent)



        except Exception,e:
            #On exception, make a request to origin server and return content to client
            print " An error has occured. So will try to forward request to Origin Server"
            try:
                oData = urllib2.urlopen(getRequest).read()
                self.returnToClient(oData)

            except urllib2.HTTPError, e:
                self.send_response(e.code)
                self.send_header('Content-type','text/html')
                self.end_headers()
                print "Error from Origin server:" + str(e.code)
                return



    def returnToClient(self,message):
        #Send content to client
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(message)
        print "contents in memory: " + str(mCache.keys())
        print "contents in disk:" + str(dCache)
        print "Mem-Cache size="+str(getContentSize(mCache, set()))
        print "Disk-Cache size="+str(getDiskSpace("."))


# This function is used to check the Size of an Object
def getContentSize(obj, s):

    cs = getContentSize
    if id(obj) in s:
        return 0
    size = getsizeof(obj)
    s.add(id(obj))
    if isinstance(0, unicode) or isinstance(obj, str):
        return size
    if isinstance(obj, Mapping):
        return size + sum(cs(key, s) + cs(val, s) for key, val in obj.iteritems())
    if isinstance(obj, Container):
        return size + sum(cs(tup, s) for tup in obj)
    return size

if __name__ == '__main__':
	main()
