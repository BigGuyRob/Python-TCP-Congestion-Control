import argparse
from sys import argv
import socket
import struct
from random import uniform
ACK_DROP = 0.5
PACK_DROP = 0.5
HALF_DROP = 0.0
tcp_header_string = '!HHIIHHHHI'
TCP_header_struct = struct.Struct(tcp_header_string)
def pack_flags(URG,ACK,PSH,RST,SYN,FIN):
	answer = 0x0000
	answer |= FIN & 0x1
	answer |= (SYN & 0x1) << 1
	answer |= (RST & 0x1) << 2
	answer |= (PSH & 0x1) << 3
	answer |= (ACK & 0x1) << 4
	answer |= (URG & 0x1) << 5
	return answer
def unpack_flags(options):
	answer_dict = {}
	answer_dict['FIN'] = options & 0x1
	options >>= 1
	answer_dict['SYN'] = options & 0x1
	options >>= 1
	answer_dict['RST'] = options & 0x1
	options >>= 1
	answer_dict['PSH'] = options & 0x1
	options >>= 1
	answer_dict['ACK'] = options & 0x1
	options >>= 1
	answer_dict['URG'] = options & 0x1
	return answer_dict
def make_TCP_PACK(sequence_number, ack_number, source_port = 0, dest_port = 0, URG= 0, ACK=0, PSH=0,RST=0,SYN=0,FIN=0, window=0, cksum=0,urgent=0,options=0):
	flags = pack_flags(URG, ACK,PSH,RST,SYN,FIN)
	checksum = 0
	header = TCP_header_struct.pack(source_port, dest_port, sequence_number, ack_number,flags, window, checksum, urgent, options)
	return header
def make_TCP_UNPACK(header):
	header_items = TCP_header_struct.unpack(header)
	# header_items[4] = unpack_flags(header_items[4])
	header_dict = {'source_port':header_items[0], 'dest_port':header_items[1], 'sequence_number':header_items[2], 'ack_number':header_items[3], 'flags':header_items[4], 'window':header_items[5], 'checksum':header_items[6], 'urgent':header_items[7], 'options':header_items[8]}
	header_dict['flags'] = unpack_flags(header_dict['flags'])
	return header_dict

def main():
	#First we use the argparse package to parse the aruments
	parser=argparse.ArgumentParser(description="""This is a very basic client program""")
	parser.add_argument('-o', type=str, help='This is the destination file for the recieved file', default='results.txt',action='store', dest='out_file')
	parser.add_argument('recv_port', type=int, help='This is the recv port', action='store')
	parser.add_argument('server_location', type=str, help='This is the domain name or ip address of the server',action='store')
	parser.add_argument('port', type=int, help='This is the port to connect to the server on',action='store')
	parser.add_argument('--window', type=int, help='This This is the window size', default=4096, action='store')
	parser.add_argument('--stop_and_wait', help='This is the recv port', const=488, action='store_const', default=0)

	args = parser.parse_args(argv[1:])
	RCV_WND = args.window
	if args.stop_and_wait:
		RCV_WND = args.stop_and_wait
	#next we create a client socket
	client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_addr = (args.server_location, args.port)
	client_sock.bind(('', args.recv_port))
	client_sock.connect(server_addr)
	recv_buffer = ['EMPTY' for x in range(RCV_WND)]
	#['EMPTY', 'EMPTY', 'a', 'c', 'EMPTY', 'EMPTY']
	#now we need to open both files
	#------- EXTRA CREDIT PART 1 HERE
	RCV_NXT = 0
	ISN_RECV = 0
	with open(args.out_file, 'wb') as write_file:
		RCV_NXT = 0
	#------- EXTRA CREDIT PART 1 END HERE
		while True:
			#recieve one packet
			packet = client_sock.recv(512)
			# print(packet)
			header = make_TCP_UNPACK(packet[:TCP_header_struct.size])
			packet = packet[TCP_header_struct.size:]
			#----- EXTRA CREDIT PART 2 START HERE
			if header['flags']['FIN']:
				break
			#----- EXTRA CREDIT PART 2 END HERE
			if uniform(0,1) < PACK_DROP:
				continue
			elif uniform(0,1) < HALF_DROP and len(packet) > 100:
				packet = packet[:round(len(packet) / 2)]
			SEG_LEN = len(packet)
			SEG_SEQ = header['sequence_number']
			if SEG_SEQ >= RCV_NXT and SEG_SEQ <= RCV_NXT + RCV_WND:
				dest = SEG_SEQ - RCV_NXT
				message_bytes = list(packet[:RCV_WND])
				while dest < RCV_WND and message_bytes:
					recv_buffer[dest] = message_bytes.pop(0)
					dest += 1
			if SEG_SEQ + SEG_LEN - 1 >= RCV_NXT and SEG_SEQ + SEG_LEN - 1 <= RCV_NXT + RCV_WND:
				dest = SEG_SEQ - RCV_NXT
				# print(recv_buffer[:10], dest, SEG_SEQ, RCV_NXT, packet)
				message_bytes = list(packet)
				# print(message_bytes[0], tmp[SEG_SEQ])
				while message_bytes and dest < RCV_WND:
					if dest >= 0:
						recv_buffer[dest] = message_bytes.pop(0)
					else:
						message_bytes.pop(0)
					dest += 1
			while recv_buffer[0] != 'EMPTY':
				write_file.write(recv_buffer.pop(0).to_bytes(1, 'big'))
				recv_buffer.append('EMPTY')
				RCV_NXT += 1
			print(RCV_NXT)
			if uniform(0,1) < ACK_DROP:
				continue
			client_sock.sendto(make_TCP_PACK(ISN_RECV, RCV_NXT, ACK=1), server_addr)

	#close the socket (note this will be visible to the other side)
		while recv_buffer[0] != 'EMPTY':
			write_file.write(recv_buffer.pop(0).to_bytes(1, 'big'))
			recv_buffer.append('EMPTY')
			RCV_NXT += 1
	client_sock.close()
if __name__ == '__main__':
	main()
