import argparse
from cmath import exp
from re import L
import time
from sys import argv
import socket

import select

import struct
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
parser.add_argument('window_size', type = int, help='This is the window size',action='store')

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
SENT_BUFF = 0

#we are reading text from this text file from project gutenberg "The Little White Gate"
r.seek(0,SOF)
numPacket = 0

#This function creates the packets of the size the size that fills the window 
def createWindow(readFile,LSN,SENT_BUFF):
    SectionOfText = ''
    x = 0
    SEQUENCE = LSN
    #x is the last sequence number, or where we want to start the
    readFile.seek(LSN,SOF)
    data = []
    windowPackets = []
    
    while (True):
        #print(SectionOfText)
        size = MAXNUMBYTES 
        x += size
        #If the current size of all packets in the window would be greater than the window size - sent buffer - header length we need to truncate the packet
        if(x > args.window_size - SENT_BUFF - TCPHEADERLENGTH):
            x-= size
            difference = args.window_size - x - SENT_BUFF
            size = difference
            try:
                SectionOfText = readFile.read(size - TCPHEADERLENGTH)
            except ValueError:
                SectionOfText = ''
            x+=size
            data.append(SectionOfText)
            break
        else:
            SectionOfText = readFile.read(size - TCPHEADERLENGTH)
            data.append(SectionOfText)
    #^Makes the packets for the window - dont touch
    for packet in data:
        if(packet == ''):
            break
        header = make_TCP_PACK(SEQUENCE, ACK, args.port, args.recvport)
        TCPPACKET = header + packet
        #print(header) 
        windowPackets.append(TCPPACKET)
        SEQUENCE = SEQUENCE + len(packet)
    #Creates the TCP Packets^
    return windowPackets, SEQUENCE
    #As long as we can write we send to the receiver
    #onces we finish, remove
        


with r as readFile:    
    # len(SectionOfText) This should be 488 since 512 is the max that the receiver can recieve + the TCP header
    client_sock.setblocking(False)
    inputs = [client_sock]
    outputs = [client_sock]
    rec_acks = []
    prevAck = ACK
    timers = []
    flag = True
    while ACK < fileSize:
        readable,writable,exceptional = select.select(inputs,outputs,inputs,0.1) 
        #Before we send anything we want to check for the packets that have timed out
        for s in writable:
            if(timers):
                t = time.time()
                timeouts = []
                for tim in timers:
                    timeouts.append(tim[0])
                if(t > min(timeouts)): #if time is greater than the oldest time out
                    SENT_BUFF = 0
                    SEQUENCE = ACK
                    timers.clear()
                    rec_acks.clear()
                    print("something timed out now since " + str(min(timeouts)) + " > " + str(t))
            for ack in rec_acks:
                #If the ack we receiver is less than the sequence number, make sure its timer hasn't expired
                acknowledgedBytes = ack - prevAck
                prevAck = ack
                SENT_BUFF = SENT_BUFF - (acknowledgedBytes + TCPHEADERLENGTH) 
            rec_acks.clear()

            if(SENT_BUFF < args.window_size):
                packetsToSend,SEQUENCE = createWindow(readFile, SEQUENCE,SENT_BUFF)
                for tcpPacket in packetsToSend:
                    client_sock.sendto(tcpPacket,server_addr)
                    SENT_BUFF += len(tcpPacket)
                    p = make_TCP_UNPACK(tcpPacket[:TCP_header_struct.size])
                    expected = p['sequence_number'] + len(tcpPacket) - TCPHEADERLENGTH
                    print("sending packet with sequence number " + str(p['sequence_number']) + " Send buffer currently holds " + str(SENT_BUFF) + "will be expecting ACK "+ str(expected))
                    TIMEOUT = time.time() + 0.1 # When we send a packet we save the timer and its sequence number
                    timers.append([TIMEOUT,expected])
            else:
                break

        for client_sock in readable:
            recPacket = client_sock.recv(MAXNUMBYTES)
            header = make_TCP_UNPACK(recPacket[:TCP_header_struct.size])
            ACK = header['ack_number']
            rec_acks.append(ACK)
            flag = False
            #If we get a valid ack that we were expecting^ 
            print("Receiving packets with ACK " + str(ACK))
            for i in timers:# 0 - Timeout time 1 - expectedACK
                if i[1] <= ACK:
                    if(i[1] == ACK):
                        flag = True
                    timers.remove(i)
                    #If the ack is in the timers then we can continue
                    #If we get here we either got a dup ack or a half packet
            break

        for client_sock in exceptional:
            break

            
    print("File finished transferring " + str(ACK) + " number of bytes")
    client_sock.close()