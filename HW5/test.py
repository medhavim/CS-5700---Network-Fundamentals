'''
Created for Roll you onw CDN project
@authors: Kaustubh Pande, Harshad Sathe

'''
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import collections
import urllib2
import sys
import zlib
import tarfile
import os
import signal

local_cache = {}
contents = 0
originServer = 0

class createLocalCache():
    def __init__(self):
        self.url = ''
        self.data = ''
        self.content_type = ''

    #Implements assigning of values to a Cache Entry Object after creation
    def add_CacheEntry (self, url, data, content_type):
        self.data = zlib.compress(data)
        self.content_type = content_type
        if url == '/':
            url = "/index"
        self.url = url

    #Implements a simple cache eviction alogorithm, based on recent use of the URL
    def implement_cache_evict(self,URL):
        global local_cache, contents

        for key, value in local_cache.items():
            #evicted_obj = value
            evicted_URL = str(local_cache.keys()[0])
            contents = contents - len(value.data)
            del local_cache[evicted_URL]
            expected_content_size = contents + len(self.data)
            if expected_content_size < 10000000:
                break

        local_cache[URL] = self
        contents = contents + len(self.data)

    # GET content from the Origin Server
    def download_content_from_Origin(self,handler_obj, URL, MIME):
        handler_obj.send_response(200)
        handler_obj.send_header('Content-type',MIME)
        handler_obj.end_headers()
        html_data = urllib2.urlopen(URL).read()
        handler_obj.wfile.write(html_data)
        return html_data

    #On cache miss, this function opens a new URL,GET the data from
    #ORIGIN SERVER
    def get_data_from_Origin (self, handler_obj, URL, mimetype, path):
        global local_cache, contents
        html_data = self.download_content_from_Origin(handler_obj,URL,mimetype)
        self.add_CacheEntry(path, html_data, mimetype)

        if len(self.data) < 10000000:
            if (contents + len(self.data)) > 10000000:
                self.implement_cache_evict(URL)
            else:
                contents = contents + len(self.data)
                local_cache[URL] = self

# Custom HTTP Handler class, called when the HTTP request is sent from the client
class Custom_HTTP_Handler(BaseHTTPRequestHandler):
    global local_cache, contents
    cache_content_ref = createLocalCache()

    #Automatically invoked, when the port listens to incoming HTTP request
    def do_GET(self):
        self.ORIGINSERVER = originServer
        RequestURL = 'http://' + self.ORIGINSERVER + ':8080' + str(self.path)

        # Removes the cache entry for the URL
        def handleLocalCache():
            cache_content = local_cache[RequestURL]
            del local_cache[RequestURL]
            return cache_content

        # Writes the content to a file.
        def download_content(self, cache_content_obj):
            html_content = zlib.decompress(cache_content_obj.data)
            self.wfile.write(html_content)
            return

        try:
            if RequestURL in local_cache:

                cache_content_obj = handleLocalCache()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                local_cache[RequestURL] = cache_content_obj

                download_content(self, cache_content_obj)
            else:
                self.cache_content_ref.get_data_from_Origin(self, RequestURL, "text/html", self.path)
                return
        except IOError:
            self.send_error(404,'Filepath Not Found in the origin server {0}'.format(self.path))

# Class handles the HTTP requests and listens on the provided port number
class Http_Server():

    def handle_termination(self, signal, frame):
            self.persist_cache()
            try:
                print "In try"
            except Exception:
                error = True
            finally:
                sys.exit(0)

    # Sets the origin Server and opens port to Listen for HTTP requests, also handles persistent caching
    def listenTorequests(self, port):

        self.httpd = HTTPServer(('', port), Custom_HTTP_Handler)

        self.load_cache(originServer)

        signal.signal(signal.SIGINT, self.handle_termination)

        self.httpd.serve_forever()


    # Set Local_cache and contents values
    def initializeCache(self,origin_server):
        global local_cache, contents, originServer
        local_cache = collections.OrderedDict()
        contents = 0
        originServer = origin_server

    # Create the directories for storing persistent cache
    def handleDirectories(self):
            sourcePath  = os.path.dirname(os.path.realpath(__file__))
            directory = 'cacheDB'

            os.chdir(sourcePath)

            if not (os.path.exists(directory)):
                os.mkdir(directory)
            os.chdir(directory)

    # Compress data on the disk
    def makeTarFile(self,file_name):
        tar = tarfile.open(file_name.strip() + ".tar.gz", "w:gz")
        tar.add(file_name)
        tar.close()

    # Stores Cache data into a file on Disk
    def persist_cache(self):
        global local_cache
        self.handleDirectories()

        for entry in local_cache.items():
            cache_entry = entry[1]
            file_name = cache_entry.url[1:]
            file_name = file_name.replace('/', '@')
            fileHandle = open (file_name, "w")
            fileHandle.write(cache_entry.url+"\n")
            fileHandle.write(cache_entry.content_type+"\n")
            data = zlib.decompress(cache_entry.data)
            fileHandle.write(data)
            fileHandle.close()

            self.makeTarFile(file_name)
            os.remove(file_name)

    # Finds the persistent DB for the cache
    def get_dir_path(self):
        source_path  = os.path.dirname(os.path.realpath(__file__))
        dir_path = 'cacheDB'
        os.path.join(source_path, dir_path)
        return dir_path,source_path

    # Handle URL parsing
    def handleURL_from_Cache(self, file_name, source_path, origin_server):
        url = file_name.replace('@', '/')
        if url == "index":
            url = ''

        url = str('http://')+origin_server+str(':8080/')+url
        return url

    # Get the actual compressed data from the file
    def get_content_from_cache_file(self, file_name, string_data):
        fileHandle = open (file_name, "r")

        content = fileHandle.readline()
        relative_url = content.strip()
        content = fileHandle.readline()
        content_type = content.strip()
        while True:
            tempData = fileHandle.readline()
            string_data += tempData
            if not tempData:
                break

        return relative_url, string_data, content_type

    # Load Data from Persistent File into in-memory Cache
    def load_cache (self,origin_server):
        global local_cache
        directory,source_path = self.get_dir_path()
        string_data = ''

        if os.path.exists(directory):
            os.chdir(directory)

            for cacheFile in os.listdir(os.curdir):
                tar = tarfile.open(cacheFile, "r:gz")
                fileSplit = cacheFile.split(".")
                file_name = fileSplit[0]
                tar_temp = file_name + ".tar.gz"
                tar.extract(file_name)
                cacheItem = createLocalCache()

                url = self.handleURL_from_Cache(file_name, source_path, origin_server)

                os.path.join(source_path, file_name)

                relative_url, string_data, content_type = self.get_content_from_cache_file(file_name, string_data)

                cacheItem.add_CacheEntry(relative_url, string_data, content_type)

                local_cache[url] = cacheItem

                os.remove(file_name)
                os.remove(tar_temp)
            os.chdir(source_path)
            os.rmdir(directory)

def main():
    try:
        port_number = int(sys.argv[2])
        origin_server = sys.argv[4]
    except:
        print "Usage ./httpserver.py -p [PORT] -o [origin server]"
        sys.exit()

    httpservObj = Http_Server()
    try:
        httpservObj.initializeCache(origin_server)
        httpservObj.listenTorequests(port_number)
    except KeyboardInterrupt:
        httpservObj.persist_cache()
        exit()

if __name__ == '__main__':
   main()
