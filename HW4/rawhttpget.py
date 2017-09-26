############################# TCP HEADER ########################################
#0                   1                   2                   3   
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |          Source Port          |       Destination Port        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                        Sequence Number                        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Acknowledgment Number                      |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |  Data |           |U|A|P|R|S|F|                               |
#   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
#   |       |           |G|K|H|T|N|N|                               |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |           Checksum            |         Urgent Pointer        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Options                    |    Padding    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                             data                              |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#################################################################################


############################# IP HEADER #########################################
#0                   1                   2                   3   
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |Version|  IHL  |Type of Service|          Total Length         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |         Identification        |Flags|      Fragment Offset    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |  Time to Live |    Protocol   |         Header Checksum       |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                       Source Address                          |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Destination Address                        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                    Options                    |    Padding    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#################################################################################

# importing the required libraries
import socket
import sys
import os
import re 
import random
import urlparse
import time
from struct import *

valid_HTTP_code = '200 OK'
#####################################################################
# Name: create_raw_packet
# Input: socket domain, socket type, socket protocol
# Output: socket
# Details: This functions creates a socket based on the 
#          parameters provided
#####################################################################
def create_raw_socket(domain, type, protocol):
    try:
	sock = socket.socket(domain, type, protocol)
    except socket.error, msg:
	print 'Socket could not be created. Error Code: ' + str(msg[0]) + ' Message: ' + str(msg[1])
	sys.exit()
    return sock

#####################################################################
# Name: generate_syn 
# Input: sending socket, source and destination IP and posrt number 
# Output: None 
# Details: Sends out a SYN message via the provided sending socket 
#####################################################################
def generate_syn(send_sock, source_ip, dest_ip, src_port):
    # Constructing the sending packet
    sending_packet = ''
    
    # Construct the packet with byte ordering  
    ip_header = create_ip_header(54321, source_ip, dest_ip)
    
    #Parameters passed to the function are port, seq, ackno, fin_flag, syn_flag, rst_flag, psh_flag, ack_flag respectively.
    tcp_header = create_tcp_header(src_port, 0, 0, 0, 1, 0, 0, 0)
    
    # Get Tcp header with create_tcp_header_with_checksum
    tcp_header = create_tcp_header_with_checksum(tcp_header, src_port, 0, 0, 0, 1, 0, 0, 0, source_ip, dest_ip, '')
    
    # final full packet - syn packets dont have any data
    sending_packet = ip_header + tcp_header
    
    #Send the packet finally - the port specified has no effect
    send_sock.sendto(sending_packet, (dest_ip, 0)) 

    # To keep track of packets to be resent
    global start_time
    start_time = time.time()
#####################################################################
# Name: ip_of_localhost 
# Input: None 
# Output: source IP address   
# Details: Finds the source IP address 
#####################################################################
def ip_of_localhost() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = ''
    host_temp = 'www.ccs.neu.edu'
    try:
        sock.connect((host_temp, 9))
        ip = sock.getsockname()[0]
    except socket.error:
        ip = "Unknown IP"
    finally:
	sock.close()
    return str(ip)

#####################################################################
# Name: checksum 
# Input: Message 
# Output: checksum value
# Details: This function calculates the checksum based on the length 
# of the input message 
#####################################################################
def checksum(msg):
    csum = 0
  
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        wr = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        csum = csum + wr
   
    csum = (csum>>16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
   
    #complement and mask to 4 byte short
    csum = ~csum & 0xffff
   
    return csum 

#####################################################################
# Name: write_to_file 
# Input: filename, dictionary which has the recieved data 
# Output: None 
# Details: This function writes the data and the body of the HTML recieved 
# into the file name provided 
#####################################################################
def write_to_file(fp, response_dictionary):
    proper_sequence = sorted(response_dictionary.iterkeys())
    http_response = ""
    for key in sorted(response_dictionary):
	http_response = http_response + response_dictionary[key] 
    
    srch_obj = re.search(valid_HTTP_code, http_response, re.I)
    if not srch_obj:
        print "Error: Bad HTTP Response!"
        sys.exit()
    else:
        writefile = open (fp, "w")
        counter = 0
        for seq in proper_sequence:
            if counter == 0:
                str = response_dictionary[seq]
                writefile.writelines(str.split('\r\n\r\n')[1])
                #inside the file function
                counter = counter + 1
            else:
                writefile.writelines(response_dictionary[seq])

#####################################################################
# Name: create_ip_header 
# Input: packet ID, source and destination IP 
# Output: ip_header 
# Details: Creates the packed IP header based on the input given 
#####################################################################
def create_ip_header(packet_id, src_ip, dst_ip):
    IP_HEADER_LEN = 5
    IP_VERSION = 4
    IP_TYPE_OF_SERVICE = 0
    IP_TOTAL_LENGTH = 0
    IP_ID = packet_id   
    IP_FRAGMENTAION_OFFSET = 0
    IP_TTL = 255
    IP_PROTOCOL = socket.IPPROTO_TCP
    IP_CHECKSUM = 0   
    IP_SRC_ADDR = socket.inet_aton(src_ip)
    IP_DST_ADDR = socket.inet_aton(dst_ip)
    IP_IHL_VER = (IP_VERSION << 4) + IP_HEADER_LEN
    ip_header = pack('!BBHHHBBH4s4s', IP_IHL_VER, IP_TYPE_OF_SERVICE, IP_TOTAL_LENGTH, IP_ID, IP_FRAGMENTAION_OFFSET, IP_TTL, IP_PROTOCOL, IP_CHECKSUM, IP_SRC_ADDR, IP_DST_ADDR)
    return ip_header

#####################################################################
# Name: create_tcp_header 
# Input: Port number, sequence number, acknowledgement number,
# FIN, SYN, RST, PSH and ACK flag values 
# Output: tcp_header 
# Details: Creates the packed TCP header based on the input given  
#####################################################################
def create_tcp_header(src_port, seq, ackno, fin_flag, syn_flag, rst_flag, psh_flag, ack_flag):
    TCP_SOURCE = src_port  
    TCP_DEST = 80  
    TCP_SEQ = seq
    TCP_ACK_SEQ = ackno
    TCP_DOFF = 5    
    #tcp flags
    TCP_FIN = fin_flag
    TCP_SYN = syn_flag
    TCP_RST = rst_flag
    TCP_PSH = psh_flag
    TCP_ACK = ack_flag
    TCP_URG = 0
    TCP_WINDOW = socket.htons(5840) 		#maximum allowed window size
    TCP_CHECKSUM = 0
    TCP_URG_PTR = 0
    TCP_OFFSET_RES = (TCP_DOFF << 4) + 0
    TCP_FLAGS = TCP_FIN + (TCP_SYN << 1) + (TCP_RST << 2) + (TCP_PSH <<3) + (TCP_ACK << 4) + (TCP_URG << 5)
    tcp_header = pack('!HHLLBBHHH' , TCP_SOURCE, TCP_DEST, TCP_SEQ, TCP_ACK_SEQ, TCP_OFFSET_RES, TCP_FLAGS,  TCP_WINDOW, TCP_CHECKSUM, TCP_URG_PTR)
    return tcp_header

#####################################################################
# Name: create_tcp_header_with_checksum 
# Input: header, Port number, sequence number, acknowledgement number,
# FIN, SYN, RST, PSH and ACK flag values, source and destionation IP and
# data to be sent 
# Output: tcp_header 
# Details: Creates the packed TCP header with the checksum details
# based on the input given 
#####################################################################
def create_tcp_header_with_checksum(tcp_header, src_port, seq, ackno, fin_flag, syn_flag, rst_flag, psh_flag, ack_flag, source_ip, dest_ip, data):
    TCP_SOURCE = src_port  
    TCP_DEST = 80  
    TCP_SEQ = seq
    TCP_ACK_SEQ = ackno
    TCP_DOFF = 5    
    #tcp flags
    TCP_FIN = fin_flag
    TCP_SYN = syn_flag
    TCP_RST = rst_flag
    TCP_PSH = psh_flag
    TCP_ACK = ack_flag
    TCP_URG = 0
    TCP_WINDOW = socket.htons(5840)             #maximum allowed window size
    TCP_CHECKSUM = 0
    TCP_URG_PTR = 0
    TCP_OFFSET_RES = (TCP_DOFF << 4) + 0
    TCP_FLAGS = TCP_FIN + (TCP_SYN << 1) + (TCP_RST << 2) + (TCP_PSH <<3) + (TCP_ACK << 4) + (TCP_URG << 5)
        
    request_data = data
    # pseudo header fields
    s_addr = socket.inet_aton(source_ip)
    d_addr = socket.inet_aton(dest_ip)
    placehold = 0
    used_prtcl = socket.IPPROTO_TCP
    length_of_tcp = len(tcp_header) + len(request_data)
 
    #packing the packet
    packet_maker = pack('!4s4sBBH' , s_addr , d_addr , placehold , used_prtcl , length_of_tcp)
    packet_maker = packet_maker + tcp_header + request_data
 
    TCP_CHECKSUM = checksum(packet_maker)
 
    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBH' , TCP_SOURCE, TCP_DEST, TCP_SEQ, TCP_ACK_SEQ, TCP_OFFSET_RES, TCP_FLAGS,  TCP_WINDOW) + pack('H' , TCP_CHECKSUM) + pack('!H' , TCP_URG_PTR)
    return tcp_header

#####################################################################
# Name: send_ack 
# Input: sending socket, port number, source and destination
# IP address and the TCP headers 
# Output: None 
# Details: Sends an acknowledgement 
#####################################################################
def send_ack(send_sock, src_port, source_ip, dest_ip, tcph):
    acknowledgement_packet = ''
    # Incrementing the SYN packetId by 1 and sending it out.
    ip_header = create_ip_header(54322, source_ip, dest_ip)
    # tcp header fields
    tcp_source_port = src_port  # source port
    tcp_seq = tcph[3]
    tcp_ack_seq = tcph[2] + 1
    #tcp flags
    tcp_fin = 0
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 1
            
    # the ! in the pack format string means network order
    tcp_header = create_tcp_header(tcp_source_port, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack)
    tcp_header = create_tcp_header_with_checksum(tcp_header, tcp_source_port, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack, source_ip, dest_ip, '')
    acknowledgement_packet = ip_header + tcp_header 
    
    send_sock.sendto(acknowledgement_packet, (dest_ip, 0)) 

#####################################################################
# Name: get_synack_send_ack 
# Input: sending and recieving socket, buffer size,
# source and destination IP address and the port number 
# Output: TCP Header value 
# Details: This function recieves the data of the request
# and the unpacks the data and sends the acknowledgement 
#####################################################################
def get_synack_send_ack(send_sock, recv_sock, buffer_size, source_ip, dest_ip, src_port):

    #starting an infinite loop
    while True:
        received_packet = recv_sock.recvfrom(buffer_size)
        #packet string from tuple
        received_packet = received_packet[0]
        #take first 20 characters for the ip header
        ip_header = received_packet[0:20]
        #now unpack them
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
        ttl = iph[5]
        protocol = iph[6]
        src_addr = socket.inet_ntoa(iph[8])
        dest_addr = socket.inet_ntoa(iph[9])
        tcp_header = received_packet[iph_length:iph_length+20]
   
        #now unpack them
        tcph = unpack('!HHLLBBHHH' , tcp_header)
   
        #src_port = tcph[0]
        dest_port = tcph[1]
        seq_number = tcph[2]
        doff_reserved = tcph[4]
        tcph_length = doff_reserved >> 4
   
   
        h_size = iph_length + tcph_length * 4
        data_size = len(received_packet) - h_size
        #get data from the packet
        data = received_packet[h_size:]
        if src_addr == dest_ip and dest_addr == source_ip and tcph[5] == 18 and src_port == tcph[1] and ((start_time-time.time())<60):
            send_ack(send_sock, src_port, source_ip, dest_ip, tcph)   
	    break
	else:
	    generate_syn(send_sock, source_ip, dest_ip, src_port)   
	    break 
    return tcph

#####################################################################
# Name: send_request_for_file 
# Input: sending socket, source and destination IP address,
# port number, TCP header flags, The URL to be requested 
# and the host from where the file is being requested  
# Output: None 
# Details: This function requests data of the given URL.
# It makes a HTTP GET request 
#####################################################################
def send_request_for_file(send_sock, source_ip, dest_ip, src_port, tcph, path_url, hostname):
    #send a HTTP Get
    httprequest_packet = ''
    ip_header = create_ip_header(54323, source_ip, dest_ip)
    # tcp header fields
    tcp_source = src_port  # source port
    tcp_seq = tcph[3]
    tcp_ack_seq = tcph[2] + 1
    #tcp flags
    tcp_fin = 0
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 1
    tcp_ack = 1

    tcp_header = create_tcp_header(tcp_source, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack)
    request_httpdata = 'GET '+path_url+' HTTP/1.0\r\nHOST: '+hostname+'\r\n\r\n'
    
    if len(request_httpdata) % 2 != 0:
        request_httpdata = request_httpdata + " "
    
    tcp_header = create_tcp_header_with_checksum(tcp_header, tcp_source, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack, source_ip, dest_ip, request_httpdata)
    httprequest_packet = ip_header + tcp_header + request_httpdata
    send_sock.sendto(httprequest_packet, (dest_ip, 0))  

##############################################################################
# Name: download_file 
# Input: sending socket, recieving socket, buffer size, source and destination IP address, 
# port number, name of the file 
# Output: None 
# Details: This function recieves the data from the destination IP address 
# of the request sent from the souce IP address on the port number given
# and saves all the data in a dictionary and writes the to the filename given 
###############################################################################
def download_file(send_sock, recv_sock, buffer_size, source_ip, dest_ip, src_port, fp):      
    response_dictionary = {}
    c = 0 
    while True:
        #receiving packet from the server
        received_packet = recv_sock.recvfrom(buffer_size)
        #packet string from tuple
        received_packet = received_packet[0]
        #take first 20 characters for the ip header
        ip_header = received_packet[0:20]
        #unpacking the packet
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
   
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
        ttl = iph[5]
        protocol = iph[6]
        src_addr = socket.inet_ntoa(iph[8])
        dest_addr = socket.inet_ntoa(iph[9])
        tcp_header = received_packet[iph_length:iph_length+20]
        #unpacking the packet
        tcph = unpack('!HHLLBBHHH' , tcp_header)
      
        #src_port = tcph[0]
        dest_port = tcph[1]
        seq_number = tcph[2]
        doff_reserved = tcph[4]
        tcph_length = doff_reserved >> 4
        flags = tcph[5]
       
        h_size = iph_length + tcph_length * 4
        data_size = len(received_packet) - h_size
        if dest_port == src_port and src_addr == dest_ip and data_size > 0:
	    c = c + 1
            #get data from the packet
            data = received_packet[h_size:]
            #storing the sequence of packets
            response_dictionary[seq_number] = data
            #packet for teardown initiation
            teardown_initiator = ''

            ip_header = create_ip_header(54322, source_ip, dest_ip)
      
            # tcp header fields
            tcp_source = src_port  # source port
            tcp_seq =  tcph[3]
            tcp_ack_seq = seq_number + data_size
            #tcp flags
            tcp_fin = 0
            tcp_syn = 0
            tcp_rst = 0
            tcp_psh = 0
            tcp_ack = 1
        
            data_for_teardown = ''
            tcp_header = create_tcp_header(tcp_source, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack)
            tcp_header = create_tcp_header_with_checksum(tcp_header, tcp_source, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack, source_ip, dest_ip, data_for_teardown)
    
            # final full packet - syn packets dont have any data
            teardown_initiator = ip_header + tcp_header + data_for_teardown
	    send_sock.sendto(teardown_initiator, (dest_ip, 0))

        if (tcph[5] == 17 or tcph[5] == 25) and dest_port == src_port and src_addr == dest_ip and data_size == 0:
            #finish the connection
            #data to be sent during finishing the connection
            fin_packet = ''
            ip_header = create_ip_header(54322, source_ip, dest_ip)
   
        
            #tcp header fields
            tcp_source = src_port  # source port
            tcp_seq =  tcph[3]
            tcp_ack_seq = seq_number + 1
            #tcp flags
            tcp_fin = 1
            tcp_syn = 0
            tcp_rst = 0
            tcp_psh = 0
            tcp_ack = 1

            #data to be sent in final packet
            data_in_finpacket = ''

            tcp_header = create_tcp_header(tcp_source, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack)
            tcp_header = create_tcp_header_with_checksum(tcp_header, tcp_source, tcp_seq, tcp_ack_seq, tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack, source_ip, dest_ip, data_in_finpacket)
    
            # final full packet - syn packets dont have any data
            fin_packet = ip_header + tcp_header + data_in_finpacket
            send_sock.sendto(fin_packet, (dest_ip, 0))
            write_to_file(fp, response_dictionary)
            break
	elif dest_port == src_port and src_addr == dest_ip and data_size == 0 and c > 0:
            write_to_file(fp, response_dictionary)
	    break

#####################################################################
# Name: get_filename 
# Input: URL of the file to be downloaded 
# Output: filename to be created and path to be requested 
# Details: This function gets the name of file to be created 
# and also the path from where it is to be requested.
# If the URL ends with '/', filename to download is index.html 
#####################################################################
def get_filename(split_url):
    fp = " "
    empty_string = ""
 #if url does not include any path, create index.html
    if split_url.path == empty_string :
        path_url = "/"
        fp = "index.html"
    else:
        length_of_path = len(split_url.path)
        last_character = split_url.path[length_of_path-1]
        #if url includes / in last, create index.html
        if last_character == "/" :
            path_url =  "/"
            fp = "index.html"
        else:
        #else create normal filename
            path_url = split_url.path
            split_name = split_url.path.rsplit("/", 1)
            fp = split_name[1]
    return fp, path_url

#####################################################################
# Name: start() 
# Input: None 
# Output: None 
# Details: The main function of this program. It creates 
# the sockets, establishes connection and downloads the 
# file provided in arguement to the current working directory 
#####################################################################
def start():
    #set a rule in iptables to drops outgoing TCP RST packets
    os.system("iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP")

    #initializing buffer to store the packets
    buffer_size = 65565
    #Generate random port numbers
    src_port=random.randint(100, 65565)
    #Storing the url which is passed as a parameter
    url_parameter = sys.argv[1]
    #url_parameter = "http://david.choffnes.com"


    #Divides the url into single strings of distinct strings
    split_url = urlparse.urlsplit(url_parameter)
    hostname = split_url.netloc 
    #storing sourceIP
    source_ip = ip_of_localhost()
    #storing destinationIP
    dest_ip = socket.gethostbyname(urlparse.urlparse(url_parameter).hostname)
    
    #Initializing variable to store the data
    fp, path_url = get_filename(split_url)
    
    # Create a send raw socket
    send_sock = create_raw_socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    
    # Create a recieve raw socket
    recv_sock = create_raw_socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
  
    # Send out a SYN Request 
    generate_syn(send_sock, source_ip, dest_ip, src_port)
    
    # Check for Syn-Ack from server. If yes, get the unwrapped TCP Header
    tcph = get_synack_send_ack(send_sock, recv_sock, buffer_size, source_ip, dest_ip, src_port)
    
    # Send out a get request for the file to the server
    send_request_for_file(send_sock, source_ip, dest_ip, src_port, tcph, path_url, hostname)
    
    # Download file from the server and tear down the connection
    download_file(send_sock, recv_sock, buffer_size, source_ip, dest_ip, src_port, fp)
    
    send_sock.close()
    recv_sock.close()
    sys.exit()

#####################################################################
# Details: Sets the main function to start() 
#####################################################################
if __name__ == "__main__":
    start()
