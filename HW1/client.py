import socket
import sys
import ssl

#########################################################################################
## Function name: extract_data
## Input: The equation to be calculated
## Output: The result of the equation
## Description: This function returns the result of the equation provided.
##	Once the last result is encountered, a Message "BYE" is provided, encountering
##	which the program exists.
##	Incase any other data encountered, the program returns an error
#########################################################################################
def extract_data(data):
    dataArray = data.split()
    if len(dataArray) == 3 or len(dataArray) == 5:
    	status = dataArray[2]
    	if status == "BYE":
        	return "EXIT"
    	num1 = int(dataArray[2])
    	operator = dataArray[3]
    	num2 = int(dataArray[4])
    	return calculate_result(num1, num2, operator)
    else:
		return "ERROR"

#########################################################################################
## Function name: calculate_result 
## Input: Two number and the operation to be performed
## Output: The result of the operation performed on the two given numbers 
## Description: This function returns the result of the operation done on the given numbers.
##  Incase any other operator encountered, the program returns an error
#########################################################################################
def calculate_result(num1,num2,operator):
    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    elif operator == "/":
        return num1 / num2
    elif operator == "^":
        return num1 ^ num2
    elif operator == "%":
        return num1 % num2
    else:
		return "ERROR"

# INPUT PARAMETERS
PORT = int(sys.argv[1])
SSL_FLAG = str(sys.argv[2])
SERVER_URL = str(sys.argv[3])
NEU_ID = str(sys.argv[4])

# FIRST MESSAGE TO THE SERVER
MESSAGE = " ".join(("cs5700fall2016","HELLO",NEU_ID,"\n"))

# CONSTANTS
BUFFER_SIZE = 1024

#########################################################################################
# Create an Unprotected TCP Socket.
# Set Socket TimeOut to 15 seconds. If the socket doesn't connect in 15 seconds, it will send a TimeOut Error.
# If SSL Flag is enabled, takes an Instance of Unprotected socket and gives a Secure Socket.
# Connect to the Server with the Secure Socket at the given address and port.
# If SSL Flag is disabled, connect with an unprotected socket. 
# Send a Message to the server with the format given in the problem.
# Receive reply from the server, Compute result and send data back to server until the program recieves a FLAG
# or an Error Occurs
# Print the Flag Recieved

#########################################################################################

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    if SSL_FLAG == "true" :
    	ssl_sock = ssl.wrap_socket(s)
    	ssl_sock.connect((SERVER_URL,PORT))
    	s=ssl_sock
    else:
    	s.connect((SERVER_URL, PORT))


    while True:
    	s.send(MESSAGE)
    	data = s.recv(BUFFER_SIZE)
    	result = extract_data(data)
    	MESSAGE = 'cs5700fall2016 ' + str(result) + '\n'
    	if result == "EXIT":
			print (data.split()[1])
			break
    	elif result == "ERROR":
			print ("Encountered an error")
			break
except:
     print ("Encountered an error")


s.close()
