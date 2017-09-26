import socket
from html.parser import HTMLParser

links_to_visit = []
visited_links = []
currenttag = ""
flags = []

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


def update_links_to_visit(attrs):
    for attr in attrs:
        if attr[0] == "href":
            if attr[1] not in links_to_visit and attr[1] not in visited_links:
                links_to_visit.append(attr[1])

def check_for_flags(attrs,data):
    for attr in attrs:
        if attr[0] == "class" and attr[1] == "secret_flag":
            flags.append(data.split(":")[1])
           

def get_response_html(response_data):
    response_html= response_data.split("\r\n\r\n")
    if len(response_html) == 2:
        return response_html[1]
  
def get_session_id_from_cookie(res_dict):
    cookie = res_dict["Set-Cookie"]
    session_id = cookie.split("=",1)[1].split(";",1)[0]
    return session_id

def build_get_request(url, session_id):
    method = "GET"
    path = url
    version = "HTTP/1.0"
    line1 = " ".join((method,path,version))
    line2 = "Host: cs5700f16.ccs.neu.edu"
    line3 = "Cookie: _ga=GA1.2.1589665353.1459380003; csrftoken=a468a1af1b73270230ba891bc4381b19; sessionid=" + session_id
    
    return "\n".join((line1,line2,line3,"\n"))
     
def get_response_headers_dict(headers_list):
    response_dict = {}
    for header in headers_list:
         split_char = ":"
         if len(header.split(split_char,1)) == 2 :
             key = header.split(split_char,1)[0]
             value = header.split(split_char,1)[1]
             response_dict[key] = value
    return response_dict

def get_response_headers(response_list):
    return response_list[1:len(response_list)-1]

def handle_response(response_status,response_list):
    response_headers_list = get_response_headers(response_list)
    response_headers_dict = get_response_headers_dict(response_headers_list)

def get_response_status(response_list):
    status = 500
    try:
        if len(response_list) > 0 :
            status_str = response_list[0].split(" ")[1]
            return int(status_str)
    except:
        print("Error Response : ")
        return status
        
def convert_to_list(response_data):
    return response_data.split("\r\n")

def process_response_data(response):
    response_data = response.decode()
    response_list = convert_to_list(response_data)
    response_status = get_response_status(response_list)
    handle_response(response_status,response_list)
    

def build_login_message():
    #Build HTTP Request Lines
    method = "POST"
    path = "/accounts/login/?next=/fakebook/"
    version = "HTTP/1.0"
    line1 = " ".join((method,path,version))
    line2 = "Content-Length: 109"   
    line3 = "Content-Type: application/x-www-form-urlencoded"
    line4 = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    line5 = "Cookie: _ga=GA1.2.1589665353.1459380003; fos.web.server=myneuweb06; runId=581335375411859121; badprotocol=1; usid=fmDLdE2TYN9sxWaqsJQdSg__; csrftoken=a468a1af1b73270230ba891bc4381b19; sessionid=53fb4e20ff662efc0c8d13b4c327e056"
    line6 = "Host: cs5700f16.ccs.neu.edu\n"
    body  = "username=001612685&password=4QBTTMZW&csrfmiddlewaretoken=a468a1af1b73270230ba891bc4381b19&next=%2Ffakebook%2F\n"

    request_message = "\n".join((line1,line2,line3,line4,line5,line6,body))
    return str(request_message)

def create_socket():
    s = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
    return s

def start():
       HOST = "cs5700f16.ccs.neu.edu"
       PORT = 80
       BUFFER_SIZE = 4096
      
       http_message = build_login_message().encode()
       count = 0 
            
       while True and len(flags) != 5 :
           socket = create_socket()
           socket.connect((HOST,PORT))
           socket.send(http_message)
           response = socket.recv(BUFFER_SIZE)
           response_str = response.decode()
           response_list = convert_to_list(response_str)
           response_headers_list = get_response_headers(response_list)
           response_headers_dict = get_response_headers_dict(response_headers_list)
                      
           if count == 0 :
               session_id = get_session_id_from_cookie(response_headers_dict)
              
           response_status = get_response_status(response_list)
 
           if response_status == 301 or response_status == 302 :
               server_url_length = len(' http://cs5700f16.ccs.neu.edu')
               get_url = response_headers_dict["Location"][server_url_length:]
               http_message = build_get_request(get_url,session_id).encode()
           
           if response_status == 200:
               response_html = get_response_html(response_str)
               parser = Parser()
               parser.feed(response_html)
             
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
                  
           
           socket.close()
           # Only to identify the first occurence and fetch session_id
           count = count + 1 
           if len(flags) == 5:
               break
       
       for flag in flags:
           print(flag)    

if __name__ == '__main__':
    start()
