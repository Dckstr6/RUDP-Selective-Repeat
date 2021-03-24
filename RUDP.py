import socket
import threading
from _thread import *
from socketserver import ThreadingMixIn
import base64

class Connection:
	buffer_size = 0
	window_size = 3
	seq_space = 6
	packet_size = 65535
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	timeoutval = 0
	send_base = 0
	send_head = 2
	send_current_packet = 0
	sending_list = {}
	receive_list = {}

	def __init__(self,buffer_size=0,window_size=0,packet_size=0,timeoutval=0):
		self.buffer_size = buffer_size
		self.window_size = window_size
		self.packet_size = packet_size
		self.timeoutval = timeoutval
		self.send_head = self.send_base + window_size


	# Method to actually send data
	def send(self,packet,target_host,port):
		packet_params = packet.packet.split('~')
		pno = packet_params[4]
		packet_bytes = packet.packet.encode("ascii")
		base64_bytes = base64.b64encode(packet_bytes)
		# base64_string = base64_bytes.decode("ascii")
		self.s.sendto(base64_bytes,(str(target_host),int(port)))
		print(f"Sent packet {pno}")

	def bind(self,target_host,port):
		self.s.bind((str(target_host),int(port)))

	def recv(self):
		while(True):
			chunk,addr = self.s.recvfrom(1024)
			# base64_string = str(chunk)
			# base64_bytes = chunk.decode("ascii")
			ascii_string_bytes = base64.b64decode(chunk)
			recvd_string = ascii_string_bytes.decode("ascii")
			packet_params = recvd_string.split('~')
			print(f"Received string {recvd_string}")
			pno = packet_params[4]
			print(f"Received Packet {pno}")
			# print("Computing Checksum.....")


	def settimeout(self):
		self.s.settimeout(self.timeoutval)

	def close(self):
		self.s.close()


class Packet:
	payload = ""
	header = "1~"
	packet = ""
	SYN = 0
	FIN = 0
	ACK = 0
	PNO = 0
	ANO = 0
	checksum = ""

	def __init__(self,SYN,FIN,ACK,PNO,ANO,payload):
		self.SYN = SYN
		self.FIN = FIN
		self.ACK = ACK
		self.header += str(SYN)
		self.header += "~"
		self.header += str(FIN)
		self.header += "~"
		self.header += str(ACK)
		self.header += "~"
		self.header += str(PNO)
		self.header += "~"
		self.header += str(ANO)
		self.header += "~"
		self.payload = payload
		self.packet += self.header
		self.packet += self.payload

	def printPacket(self):
		print(self.packet)

