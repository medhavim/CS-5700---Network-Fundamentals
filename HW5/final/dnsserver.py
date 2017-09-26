import socket
import sys
import struct
import urllib2
import ast
from math import cos, asin, sqrt
import thread

# Global constants and variables
PORT = int(sys.argv[2])
NAME = str(sys.argv[4])
BUFFER_SIZE = 1024
GEOIP_API_URL = 'http://geoip.nekudo.com/api/'
CDN_SERVERS = {'54.210.1.206','54.67.25.76','35.161.203.105','52.213.13.179','52.196.161.198','54.255.148.115','13.54.30.86','52.67.177.90','35.156.54.135'}
LAT_LON_LOOKUP = {
    '54.210.1.206': '39.0481,-77.4728', 
    '54.67.25.76': '37.3388,-121.8914',
    '35.161.203.105': '45.8696,-119.688', 
    '52.213.13.179': '53.3389,-6.2595',
    '52.196.161.198': '35.6427,139.7677', 
    '54.255.148.115': '1.2855,103.8565', 
    '13.54.30.86': '-33.8612,151.1982',
    '52.67.177.90': '-23.5464,-46.6289', 
    '35.156.54.135': '50.1167,8.6833'
    }

DISTANCE_LOOKUP = {}

GLOBAL_IP_LOOKUP = {}

#************************** ***************************************
# The Function gets the IP Address of localhost. Cannot bind to 
# 127.0.0.1
#*****************************************************************
def ip_of_localhost() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = ''
    host_temp = 'www.ccs.neu.edu'
    try:
        sock.connect((host_temp, 80))
        ip = sock.getsockname()[0]
        #print(ip)
    except socket.error:
        ip = "Unknown IP"
    finally:
        sock.close()
    return str(ip)

#*****************************************************************
# Create a server side UDP socket. 
#*****************************************************************

def create_server_socket():   
    try:
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    except:
        print("Could not create sockets !! Exiting")
        sys.exit()
    return server_socket

#*****************************************************************
# Construct the answer section of the DNS record
#*****************************************************************
def return_answer(packet,end_index,query_type,query_class,ip):
    question_section = packet[12: 12 + end_index]
    ip_parts = ip.split('.')
    ip_part1 =  int(ip_parts[0])
    ip_part2 =  int(ip_parts[1])    
    ip_part3 =  int(ip_parts[2])
    ip_part4 =  int(ip_parts[3])    
    pack_answer_section = struct.pack("!HHLHBBBB",query_type,query_class,1,4,ip_part1,ip_part2,ip_part3,ip_part4)
    return question_section, pack_answer_section

#*****************************************************************
# Get the Best CDN based on client IP using geo location
#*****************************************************************

def get_best_geo_server(ip_addr):
    global GEOIP_API_URL,CDN_SERVERS, DISTANCE_LOOKUP
    url_to_open = GEOIP_API_URL + ip_addr
    response = urllib2.urlopen(url_to_open)
    resp = response.read()
    resp = ast.literal_eval(resp)
    lat = resp["location"]["latitude"]
    lon = resp["location"]["longitude"]
    best_ip = calculate_distance_from_cdns(float(lat),float(lon))
    return best_ip

#*****************************************************************
# Calculate distance of CDNs from the Client and store
# it in a dictionary.
#*****************************************************************
def calculate_distance_from_cdns(lat1,lon1):
    global LAT_LON_LOOKUP, DISTANCE_LOOKUP
    for ipaddr in LAT_LON_LOOKUP:
        latlon = LAT_LON_LOOKUP[ipaddr].split(",")
        lat2 = float(latlon[0])
        lon2 = float(latlon[1])
        distance = haversines_formula(lat1,lon1,lat2,lon2)
        DISTANCE_LOOKUP[ipaddr] = distance 
    for key, value in sorted(DISTANCE_LOOKUP.iteritems(), key= lambda (x,y) : (y,x)):
        best_ip,dist = (key, value)
        break
    return best_ip

#*****************************************************************
# use a simplified version of haversines formula to calculate
# distance based on lats and lons.
#*****************************************************************
def haversines_formula(lat1,lon1,lat2,lon2):
    p = 0.017
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return asin(sqrt(a))

#*****************************************************************
# Process incoming packet coming from DIG command and respond to the
# sender. 
#*****************************************************************

def process_query_from_dig(sock,data):
    global NAME, GLOBAL_IP_LOOKUP
    
    packet = data[0]
    # Length byte Index
    length_byte_index = 0 
    # Begin parsing from 1st byte
    content_index_start = 1
    # The end byte till we can read the domain name.
    content_index_end = 1
    # Only to keep track of the first iteration in the loop.
    count = 0  
    # Get the question section. First 12 bytes are headers
    dns_headers = struct.unpack("!HHHHHH",packet[0:12])
    # Extract the query section of the packet. 
    query_section = packet[12:]

    while True:
        packed_domain_length = query_section[length_byte_index]
        # First byte in query section is length of domain name
        unpacked_domain_length = struct.unpack("!B", packed_domain_length)
        unpacked_domain_length = unpacked_domain_length[0]
        
        # End parsing till the length of the domain name.
        content_index_end = content_index_start + unpacked_domain_length
        # Stop parsing when length of domain name is 0
        if unpacked_domain_length == 0 :
            break
        else:     
            # Get the network order for unpacking the domain name
            network_order = str(unpacked_domain_length) + "s"
            unpack_domain_part = struct.unpack(network_order, query_section[content_index_start: content_index_end])
            domain_part =  unpack_domain_part[0]
            # get the continous set of characters based on the length of domain
            if count == 0 :
                domain = domain_part
            else:
                domain = domain + "." + domain_part

            count = count + 1 
            content_index_start = content_index_end + 1
            length_byte_index = content_index_end  

    # Check if domain name matches the incoming name argument from dig.
    if (domain.lower() == NAME.lower()) :
        IGNORE_FLAG = False
    else :
        IGNORE_FLAG = True

    # Proceed only if domain name matches the incoming name argument from dig.
    if not IGNORE_FLAG :
        # Get the query and class from the question.
        query_type = struct.unpack("!H",query_section[content_index_end : content_index_end + 2])[0]
        query_class = struct.unpack("!H",query_section[content_index_end+2 : content_index_end + 4])[0]

        # Get a lock for the resource.       
        lock = thread.allocate_lock()

        # Apply the lock for the resource.
        with lock:
            # Get the client IP from the data sent
            client_ip_addr = data[1][0]    
            # Get the best CDN for the client IP
            if client_ip_addr in GLOBAL_IP_LOOKUP :
                best_ip = GLOBAL_IP_LOOKUP[client_ip_addr]
            else:
                best_ip = get_best_geo_server(client_ip_addr)
                GLOBAL_IP_LOOKUP[client_ip_addr] = best_ip

            
        # Get the question and Answer in a packed format. 
        question, answer = return_answer(packet,content_index_end+4,query_type,query_class,best_ip)
        # Get the default 4 bytes (e.g. PktId, ...)
        first_four_bytes = packet[0:4] 
        # Get the question count [unpack(!HHHHHH, packet[0:12])[2]]
        que_count = dns_headers[2]
        ans_count = 1
        ns_count = 0
        ar_count = 0
        # Pack Question and Answer headers 
        que_ans_headers = struct.pack('!HHHH',que_count, ans_count, ns_count, ar_count) 
        # Construct the final response to be sent back
        final_response = first_four_bytes + que_ans_headers + question + "\xc0\x0c" + answer 
        # Send back to client.
        reply_to =  data[1]
        # Send the response
        sock.sendto(final_response,reply_to)
        # Close the thread
        thread.exit()
    # Close the thread
    thread.exit()

#*****************************************************************
# Create a server socket, bind to port , keep listening for
# incoming requests
#*****************************************************************
def start():
    try:
        global PORT,BUFFER_SIZE
        # create a server side socket
        server_socket = create_server_socket()
        # Get the ip address of localhost 
        ip_addr = ip_of_localhost()
        #print(ip_addr)
        # Bind server socket to a high valued port obtained from input
        server_socket.bind((ip_addr,PORT))   
        # Keep the server running forever and listen for incoming requests
        count = 0 

        while True:
            # Get the packet string
            data = server_socket.recvfrom(BUFFER_SIZE)
            # start a new thread that processes this data
            thread.start_new_thread( process_query_from_dig,(server_socket,data,)  ) 
            #exit the thread
            #thread.exit()
    except:
        print("Exception occured !! Exiting !!")

    finally :
	print("Exiting Gracefully")
        server_socket.close()

if __name__ == "__main__":
    start()


