import socket
import sys
import struct

# Global constants and variables
PORT = int(sys.argv[2])
NAME = str(sys.argv[4])
BUFFER_SIZE = 4096

#*****************************************************************
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


def process_remaining_headers():
    print("Work in Progress")

def process_query_from_dig(packet):
    dns_headers = struct.unpack("!HHHHHH",packet[0:12])
    process_remaining_headers()


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
        # Bind server socket to a high valued port obtained from input
        server_socket.bind((ip_addr,PORT))   
        
        # Keep the server running forever and listen for incoming requests
        count = 0 

        while True:
            data = server_socket.recvfrom(BUFFER_SIZE)
            # Get the packet string 
            question_packet = data[0]
            process_query_from_dig(question_packet)
           
    except EOFError,KeyboardInterrupt:
        print("Something wrong happened ! Shutting down the server !")
        server_socket.close()

if __name__ == "__main__":
    start()
