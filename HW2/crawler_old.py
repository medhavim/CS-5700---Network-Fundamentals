import socket
import sys
from html.parser import HTMLParser

## To keep track of URLs yet to be visited
links_to_visit = []

## To keep track of URLs which are already visited
visited_links = []

## To keep track of the tags encountered to get the secret flag 
currenttag = ""



## To keep track of all the secret flags found
flags = []

#############################################################
## A class that handles parsing HTML tags. The class defines
## methods to parse start tag, end tag and data between the 
## tags. 
#############################################################
class Parser(HTMLParser):

    def handle_starttag(self,tag,attrs):
        self.currenttag = tag
        self.attrs = attrs
        if tag == "a":
            update_links_to_visit(attrs)
            
    def handle_endtag(self,tag):
        pass
        
    def handle_data(self,data):
        if self.currenttag == "h2":
            check_for_flags(self.attrs,data)


#############################################################
## Function to update the links that are to be visited
#############################################################
def update_links_to_visit(attrs):
    for attr in attrs:
        if attr[0] == "href":
            if attr[1] not in links_to_visit and attr[1] not in visited_links:
                links_to_visit.append(attr[1])

#############################################################
## Function to check if the current page has any secret flags 
#############################################################
def check_for_flags(attrs,data):
    for attr in attrs:
        if attr[0] == "class" and attr[1] == "secret_flag":
            flags.append(data.split(":")[1])

#############################################################
## Function to get all the valid Fakebook URLs that need to 
## be crawled from the current page  
#############################################################
def find_crawl_url_get_message (session_id):
    found_crawl_url = False
        
    while not found_crawl_url:
        url_to_crawl = links_to_visit[len(links_to_visit) - 1]

        if '/fakebook/' == url_to_crawl:
            links_to_visit.pop()
            found_crawl_url = True
               
        if '/fakebook/' in url_to_crawl :
            links_to_visit.pop()
            visited_links.append(url_to_crawl)
            http_message = build_get_request(url_to_crawl,session_id).encode()
            found_crawl_url = True
  
        else:
            links_to_visit.pop()
            found_crawl_url = False

    #print(url_to_crawl)
    return http_message    

#############################################################
## Function to get response HTML from Raw Response from 
## server
#############################################################
def get_response_html(response_data):
    response_html= response_data.split("\r\n\r\n")
    if len(response_html) == 2:
        return response_html[1]

#############################################################
## Function to get the session ID from the cookie 
#############################################################
def get_session_id_from_cookie(res_dict):
    cookie = res_dict["Set-Cookie"]
    session_id = cookie.split("=",1)[1].split(";",1)[0]
    return session_id

#############################################################
## Function to build the get request header and body lines 
#############################################################
def build_get_request(url, session_id):
    method = "GET"
    path = url
    version = "HTTP/1.0"
    header1 = " ".join((method,path,version))
    header2 = "Host: cs5700f16.ccs.neu.edu"
    header3 = "Cookie: _ga=GA1.2.1589665353.1459380003; csrftoken=a468a1af1b73270230ba891bc4381b19; sessionid=" + session_id
    return "\n".join((header1,header2,header3,"\n"))

#############################################################
## Function to store all response key value pairs in a 
## dictionary.
#############################################################     
def get_response_headers_dict(headers_list):
    response_dict = {}
    for header in headers_list:
         split_char = ":"
         if len(header.split(split_char,1)) == 2 :
             key = header.split(split_char,1)[0]
             value = header.split(split_char,1)[1]
             response_dict[key] = value
    return response_dict

#############################################################
## Function to get response header and creating a list
#############################################################
def get_response_headers(response_list):
    return response_list[1:len(response_list)-1]

#############################################################
## Function that returns the response status from the 
## response list 
#############################################################
def get_response_status(response_list):
    status = 500
    try:
        if len(response_list) > 0 :
            status_str = response_list[0].split(" ")[1]
            return int(status_str)
    except:
        print("Error Response : ")
        return status
#############################################################
## Fucntion that converts the response data into a list
## by splitting based on a new line. 
#############################################################        
def convert_to_list(response_data):
    return response_data.split("\r\n")
  
#############################################################
## Function that builds the message to login into Fakebook
## Username and password is provided as an input to the program
#############################################################
def build_login_message():
    #Build HTTP Request Lines
    username = str(sys.argv[1])
    password = str(sys.argv[2])

    method = "POST"
    path = "/accounts/login/?next=/fakebook/"
    version = "HTTP/1.0"
    header1 = " ".join((method,path,version))
    header2 = "Content-Length: 109"   
    header3 = "Content-Type: application/x-www-form-urlencoded"
    header4 = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    header5 = "Cookie: _ga=GA1.2.1589665353.1459380003; fos.web.server=myneuweb06; runId=581335375411859121; badprotocol=1; usid=fmDLdE2TYN9sxWaqsJQdSg__; csrftoken=a468a1af1b73270230ba891bc4381b19; sessionid=53fb4e20ff662efc0c8d13b4c327e056"
    header6 = "Host: cs5700f16.ccs.neu.edu\n"
    body  = "username="+ username + "&password="+ password + "&csrfmiddlewaretoken=a468a1af1b73270230ba891bc4381b19&next=%2Ffakebook%2F\n"

    request_message = "\n".join((header1,header2,header3,header4,header5,header6,body))
    return str(request_message)

#############################################################
## Function that creates a socket
#############################################################
def create_socket():
    s = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
    return s

## The main function
def start():
       HOST = "cs5700f16.ccs.neu.edu"
       PORT = 80
       BUFFER_SIZE = 4096
       ## Flag to keep track of login
       loggedin = False
		## To login into the Fakebook account with the username and password provided
       http_message = build_login_message().encode()
       count = 0 
            
       while True and len(flags) != 5 :
			## Open socket connection
           socket = create_socket()
           socket.connect((HOST,PORT))
           socket.send(http_message)
           response = socket.recv(BUFFER_SIZE)
			
			## To get the different headers from the response message
           response_str = response.decode()
           response_list = convert_to_list(response_str)
           response_headers_list = get_response_headers(response_list)
           response_headers_dict = get_response_headers_dict(response_headers_list)
             
             
			## Get the status from the response message 
           response_status = get_response_status(response_list)

			## To handle staus codee 301 and 302 which is the HTTP redirect
			## The crawler tries again with the new URL given by the server 
           if response_status == 301 or response_status == 302 :
               if loggedin == False:
                   loggedin = True
                   session_id = get_session_id_from_cookie(response_headers_dict)
               else:
                   server_url_length = len(' http://cs5700f16.ccs.neu.edu')
                   get_url = response_headers_dict["Location"][server_url_length:]
                   http_message = build_get_request(get_url,session_id).encode()
          
			## To handle staus codee 200 which means everything is okay 
			## The crawler parses the response and moves to the next URL
           elif response_status == 200:
               response_html = get_response_html(response_str)
               parser = Parser()
               parser.feed(response_html)
               http_message = find_crawl_url_get_message(session_id)

			## To handle the status code 403 and 404 which means that 
			## the access to the page is forbidden or the page was not found respectively
			## The crawler abandons the URL that generated the error code.
           elif response_status == 403 or response_status == 404 :
               if not loggedin:
                   http_message = build_login_message().encode()
               else:
                   links_to_visit.pop()
                   http_message = find_crawl_url_get_message(session_id)   
           
			## To handle the status code 500 which means Internal Server Error occurred
			## The crawler re-tries the request for the URL until the request is successful. 
           elif response_status == 500:
                if not loggedin:
                    http_message = build_login_message().encode()
                else:
                    http_message = find_crawl_url_get_message(session_id)
           
          	## Close socket connection 
           socket.close()
           
			## Only to identify the first occurence and fetch session_id
           count = count + 1 
           if len(flags) == 5:
               break

       	## The secret flag has a space in the starting
		## this removes that extra space and prints the flags.
       for flag in flags:
           print(flag.replace(" ",""))    

## Makes start() as the main function
if __name__ == '__main__':
    start()

