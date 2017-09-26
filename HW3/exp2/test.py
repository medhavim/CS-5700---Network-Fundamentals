import os.path
import sys

## Global variables to keep track of all the packets sent and recieved 
## in a network as well the time it was sent / recieved
packets_sent_dict = {}
packets_recvd_dict = {}
packets_dropped_dict = {}
packets_recvd_tcp_dict = {}
global_time_tcp1 = 1.0
global_total_delay_tcp1 = 0
global_num_of_delay_packets_tcp1 = 0

global_time_tcp2 = 1.0
global_total_delay_tcp2 = 0
global_num_of_delay_packets_tcp2 = 0

packet_start_time_tcp1 = {}
packet_start_time_tcp2 = {}
packet_end_time = {}

## This function calculates the no.of packets needed for our analysis
def trace_count_of_packets(event,time,fromnode,tonode,pkttype,pktid):
    ## Store All packets recieved in all nodes in a dictionary
    key = str(fromnode + "-" + tonode)
    if(event == "r" and pkttype == "ack"):
        if key in packets_recvd_dict:
            packets_recvd_dict[key] = packets_recvd_dict[key] + 1
        else:
            packets_recvd_dict[key] = 1
    
    ## Store All packets sent from all nodes in a dictionary
    elif(event == "+" and pkttype == "tcp"):
        if key in packets_sent_dict:
            packets_sent_dict[key] = packets_sent_dict[key] + 1
        else:
            packets_sent_dict[key] = 1

    ## Check if packet sent is from TCP Flow 1, if yes, store start time of the packet
    ## Also, store the time of last packet sent for throughput calculations.  
    if(event == "+" and pkttype == "tcp" and fromnode == "0" and tonode == "1"):
        global global_time_tcp1
        packet_start_time_tcp1[pktid] = time
        global_time_tcp1 = time

    ## Check if packet recieved is from TCP Flow 1, if yes, calculate delay for the packet. 
    if(event == "r" and pkttype == "ack" and fromnode == "1" and tonode == "0"):
        packets_sent_dict['0-1'] = packets_sent_dict['0-1'] - 1
        if "1-0" not in packets_dropped_dict:
            packets_dropped_dict['1-0'] = packets_sent_dict['0-1'] 
        else:
            packets_dropped_dict['1-0'] = packets_sent_dict['0-1'] 
        
        global global_num_of_delay_packets_tcp1
        global global_total_delay_tcp1
        delay = 0.0
        delay = float(time) - float(packet_start_time_tcp1[pktid])
        global_total_delay_tcp1 += delay
        global_num_of_delay_packets_tcp1 = global_num_of_delay_packets_tcp1 + 1
        

    ## Check if packet sent is from TCP Flow 2, if yes, store start time of the packet
    ## Also, store the time of last packet sent for throughput calculations.  
    if(event == "+" and pkttype == "tcp" and fromnode == "4" and tonode == "1"):
        global global_time_tcp2
        packet_start_time_tcp2[pktid] = time
        global_time_tcp2 = time

    ## Check if packet recieved is from TCP Flow 2, if yes, calculate delay for the packet. 
    ## Also, store the time of last packet recieved for throughput calculations.  
    if(event == "r" and pkttype == "ack" and fromnode == "1" and tonode == "4"):
        packets_sent_dict['4-1'] = packets_sent_dict['4-1'] - 1
        if "1-4" not in packets_dropped_dict:
            packets_dropped_dict['1-4'] = packets_sent_dict['4-1'] 
        else:
            packets_dropped_dict['1-4'] = packets_sent_dict['4-1'] 
        
              
        global global_num_of_delay_packets_tcp2
        global global_total_delay_tcp2
        delay = 0.0
        delay = float(time) - float(packet_start_time_tcp2[pktid])
        global_total_delay_tcp2 += delay
        global_num_of_delay_packets_tcp2 = global_num_of_delay_packets_tcp2 + 1
        
       
## Function to calculate throughput for the flow
## Params : Time -> Time the last packet was sent for the flow
## fromnode : The Node sending packets to the recieving node in the flow
## tonode : The node recieving packets in the flow
def calculate_throughput(time, fromnode, tonode):
    key = fromnode + "-" + tonode
    PACKET_SIZE = 1040
    NO_OF_PACKETS_RECIEVED = packets_recvd_dict[key]
    throughput = (8 * NO_OF_PACKETS_RECIEVED * PACKET_SIZE / ((float(time) - float(sys.argv[4])) *1000))
    return throughput

## This function extracts the packet data from each node to node from the trace file
## Since a dictionary was used hence lne by line manipulation is done
def extract_columns_from_line(line):
    default_time = 1.0
    columns = line.split(' ')
    ## Populate the different data in the trace file
    if len(columns) >= 11:
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
    ## Calculate the throughput of each variant in the network
    throughput_tcp1 = calculate_throughput(global_time_tcp1,"1","0")
    throughput_tcp2 = calculate_throughput(global_time_tcp2,"1","4")
    ## Close the trace file
    file.close()

    ## Create an output file if not present, else append to the existing one.
    if not os.path.isfile("output_"+sys.argv[3]+".txt"):
        throughput_file = open("output_"+sys.argv[3]+".txt","w+")
    else:
        throughput_file = open("output_"+sys.argv[3]+".txt","a")

    ## Calculates the latency of the network for each variant
    avg_delay_tcp1 = global_total_delay_tcp1 / global_num_of_delay_packets_tcp1
    avg_delay_tcp2 = global_total_delay_tcp2 / global_num_of_delay_packets_tcp2
    
    packets_dropped_tcp1 = 0
    packets_dropped_tcp2 = 0

    ## to calculate the no. of packets dropped in a network
    if '1-0' in packets_dropped_dict:
        packets_dropped_tcp1 = packets_dropped_dict['1-0']

    if '1-4' in packets_dropped_dict:
        packets_dropped_tcp2 = packets_dropped_dict['1-4']

    ## Write all the details in the output file for analysis
    throughput_file.writelines("TCP Variant : " + sys.argv[3] + "   CBR:   " + sys.argv[2] + "   throughput1 :  " + str(throughput_tcp1/1000) + "   throughput2 :  " + str(throughput_tcp2/1000) + "   delay1 :  " + str(avg_delay_tcp1*1000) + "   delay2 :  " + str(avg_delay_tcp2*1000) + " Packets dropped TCP1 : " + str(packets_dropped_tcp1) + "   dropped TCP2 : " + str(packets_dropped_tcp2)  +"\n")

## Call start() as the main function
if __name__ == "__main__":
    start()
