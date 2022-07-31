import argparse
from sys import argv
import socket
import struct
from random import uniform
from receiver import make_TCP_PACK
from receiver import make_TCP_UNPACK

tcp_header_string = '!HHIIHHHHI'
TCP_header_struct = struct.Struct(tcp_header_string)
SOF = 0  #offset is relative to start of file
CPOF = 1  #offset is relative to current position
EOF = 2  #offset is relative to end of file
parser=argparse.ArgumentParser(description="""This is a very basic client program""")
parser.add_argument('-o', type=str, help='This is the destination file for the recieved file', default='results.txt',action='store', dest='out_file')
parser.add_argument('recvport', type=int, help='This is the port to recv data on',action='store')
parser.add_argument('receiver_location', type=str, help='This is the domain name or ip address of the server',action='store')
parser.add_argument('port', type=int, help='This is the port to send data on', action='store')

args = parser.parse_args(argv[1:])
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = (args.receiver_location, args.port)
client_sock.bind(('', args.recvport))
client_sock.connect(server_addr)
#I want the size of the file
r = open("lwg.txt","rb")
r.seek(0, EOF)
fileSize = r.tell()
print("Size of file is :", fileSize, "bytes")
MAXNUMBYTES = 512; 
SEQUENCE = 0
ACK = 0
TCPHEADERLENGTH = 24
#We are reading text from this text file from project gutenberg "The Little White Gate"
r.seek(0,SOF)
numPacket = 0
with r as readFile:
    SectionOfText = readFile.read(MAXNUMBYTES - TCPHEADERLENGTH)
    # len(SectionOfText) This should be 488 since 512 is the max that the receiver can recieve + the TCP header
    while(True):
        if(ACK >= fileSize):
            #The ACK number is the start of the byte of the next packet
            #We use this informaiton to stop the loop once we reach the file size
            break
        #First we have to make a packet
        tcpPacket = make_TCP_PACK(SEQUENCE, ACK, args.port, args.recvport)
        #PRINT SENT PACKET
        #print(make_TCP_UNPACK(tcpPacket))
        #-------------------------------
        tcpPacket += SectionOfText
        client_sock.sendto(tcpPacket, server_addr)
        print("SEND")
        #For the stop and wait the sender should STOP and have the recv be a blocking call
        try:
            client_sock.settimeout(0.1)
            newPacket = client_sock.recv(MAXNUMBYTES)
        
            print("ACK")
            header = make_TCP_UNPACK(newPacket[:TCP_header_struct.size])
            numPacket+=1
            ACK = header['ack_number']
            SEQUENCE += len(SectionOfText)
            #PRINT ACKNOLWEDGMENT PACKET
            #print(header)
            #--------------------------
            readFile.seek(ACK,SOF)
            SectionOfText = readFile.read(MAXNUMBYTES - TCPHEADERLENGTH)    
        except socket.timeout:
            print('No ACK received in timeout window. Resending packet.')
    print("File finished transferring in " + str(numPacket) + " packets")
    tcpPacket = make_TCP_PACK(SEQUENCE,0,args.port, args.recvport, FIN =1)
    client_sock.sendto(tcpPacket, server_addr)
    client_sock.close()
