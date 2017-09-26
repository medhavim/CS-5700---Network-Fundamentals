import sys
import urllib2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import os
from sys import getsizeof
from SocketServer import ThreadingMixIn


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

MAX_DISK_SPACE = 10000000
MAX_MEM_SPACE =  10000000

print 'MAX_DISK_SPACE = '+ str(MAX_DISK_SPACE)
httpServer = ''
originServerPort = 8080
originServerHost = 'ec2-54-167-4-20.compute-1.amazonaws.com'


def main():
    global originServerHost
    global originServerPort
    global MAX_DISK_SPACE

    if len(sys.argv) < 5:
        print "USAGE:  ./httpserver -p <port> -o <origin>"
        #   sys.exit(0)
    httpServerPort = int(sys.argv[2])
    originServerHost = sys.argv[4]

    originServerPort = 8080

    MAX_DISK_SPACE = 10000000 - getDiskSpace(".")

    httpServer = ThreadedHTTPServer(('',httpServerPort),myHandlerClass)
    s = httpServer.socket.getsockname()
    print "Serving HTTP on", s[0], "port", s[1], "..."
    try:
        print 'OriginServer=' + originServerHost
        httpServer.serve_forever()
    except:
        print "Exception"

    finally:
        print 'Exiting Gracefully'
	httpServer.shutdown()
        httpServer.socket.close()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Trying to handle parallel requests"""



class myHandlerClass(BaseHTTPRequestHandler):
    global originServerHost
    global originServerPort


    def do_GET(self):

        #resource to GET
        rs = self.path
	print(rs)


        filename = rs[1:]
        filename = filename.replace("/","_")


        #Frame GET request
        getRequest = 'http://'+originServerHost+':'+str(originServerPort)+rs
        print 'GET REQUEST=' + getRequest

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


# This function is used to check the Size of an Object
def getContentSize(obj, s):

    cs = getContentSize
    if id(obj) in s:
        return 0
    size = getsizeof(obj)
    s.add(id(obj))
    return size

if __name__ == '__main__':
	main()
