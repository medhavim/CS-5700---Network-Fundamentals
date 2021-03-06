import os.path
import sys

## Global variables to keep track of all the packets sent and recieved 
## in a network as well the time it was sent / recieved
packets_sent_dict = {} 
packets_recvd_dict = {}
packets_dropped_dict = {}
packets_recvd_tcp_dict = {}
global_time = 1.0
global_total_delay = 0
global_num_of_delay_packets = 0

packet_start_time = {}
packet_end_time = {}

## This function calculates the no.of packets needed for our analysis
def trace_count_of_packets(event,time,fromnode,tonode,pkttype,pktid):
    global global_time
    key = str(fromnode + "-" + tonode)
    
    ## If an ack is recieved at the node
    if(event == "r" and pkttype == "ack"):
        if key in packets_recvd_dict:
            packets_recvd_dict[key] = packets_recvd_dict[key] + 1 
        else:
            packets_recvd_dict[key] = 1
        global_time = time
       
    ## If an tcp is added to the queue at the node
    elif(event == "+" and pkttype == "tcp"):
        if key in packets_sent_dict:
            packets_sent_dict[key] = packets_sent_dict[key] + 1 
        else:
            packets_sent_dict[key] = 1

    ## If an tcp is dropped at the node
    elif(event == "d" and pkttype == "tcp"):
        if key in packets_dropped_dict:
            packets_dropped_dict[key] = packets_dropped_dict[key] + 1 
        else:
            packets_dropped_dict[key] = 1

    ## If an tcp is added from node N1 to node N2
    if(event == "+" and pkttype == "tcp" and fromnode == "0" and tonode == "1"):
        packet_start_time[pktid] = time

    ## If an ack is recieved from node N2 to node N1
    if(event == "r" and pkttype == "ack" and fromnode == "1" and tonode == "0"):
        global global_num_of_delay_packets
        global global_total_delay
        delay = 0.0
        delay = float(time) - float(packet_start_time[pktid])
        global_total_delay += delay
        global_num_of_delay_packets = global_num_of_delay_packets + 1
        

## this function calculates the throughput of the network 
def calculate_throughput(time):
    PACKET_SIZE = 1040
    NO_OF_PACKETS_RECIEVED = packets_recvd_dict['2-1']
    throughput = (8 * NO_OF_PACKETS_RECIEVED * PACKET_SIZE / ((float(time) - float(sys.argv[4])) *1000))
    return throughput
   
## This function extracts the packet data from each node to node from the trace file
## Since a dictionary was used hence lne by line manipulation is done 
def extract_columns_from_line(line):
    default_time = 1.0
    columns = line.split(' ')
    if len(columns) >= 11:
        ## Populate the different data in the trace file
        event = columns[0]
        time = columns[1]
        fromnode = columns[2]
        tonode = columns[3]
        pkttype = columns[4]
        pktsize = columns[5]
        flags = columns[6]
        fid = columns[7]
        srcaddr = columns[8]
        dstaddr = columns[9]
        seqnum = columns[10]
        pktid = columns[11]
        ## Gives the details of the no. of packets
        trace_count_of_packets(event,time,fromnode,tonode,pkttype,seqnum)
        return time
    return default_time

## This finction calculates the time when the last packet was sent
def process_line_by_line(data):
    data =  data.decode()
    arr_of_lines = data.split("\n")
    last_packet_time = 1.0
    for line in arr_of_lines:
        time = extract_columns_from_line(line)
        if time != 1.0:
            last_packet_time = time
    return last_packet_time

## Main function
def start():
    filename = sys.argv[1]
    ## Read the trace file
    file = open(filename,"rb+")
    ## Read the trace file line by line
    s = file.read()
    ## The time of the last packet sent 
    time = process_line_by_line(s)
    ## Calculate the throughput of the network
    throughput = calculate_throughput(global_time)
    ## Close the trace file
    file.close()
    
    ## Create an output file if not present, else append to the existing one.
    if not os.path.isfile("output_"+sys.argv[3]+".txt"):
        throughput_file = open("output_"+sys.argv[3]+".txt","w+")
    else:
        throughput_file = open("output_"+sys.argv[3]+".txt","a")
    
    ## Calculates the latency of the network
    avg_delay = global_total_delay / global_num_of_delay_packets

    packets_dropped = 0

    ## to calculate the no. of packets dropped in a network
    if '1-2' in packets_dropped_dict:
        packets_dropped = packets_dropped_dict['1-2']

    ## Write all the details in the output file for analysis
    throughput_file.writelines("TCP Variant : " + sys.argv[3] + "   CBR:   " + sys.argv[2] + "   throughput :  " + str(throughput/1000) + "   delay :  " + str(avg_delay*1000) + " Packets dropped : " + str(packets_dropped)  +"\n")
    print("CBR: "+ sys.argv[2] )

## Call start() as the main function
if __name__ == "__main__":
    start()

