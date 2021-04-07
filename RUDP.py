import socket
import threading
from _thread import *
from socketserver import ThreadingMixIn
import base64
import mmh3
import time
import os

class Connection:
	buffer_size = 0
	window_size = 0
	max_retransmits = 0
	send_base = 0
	send_head = 0
	packet_size = 0
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	timeoutval = 0

	def __init__(self,buffer_size=0,window_size=3,packet_size=1024,timeoutval=30,max_retransmits = 5):
		self.buffer_size = buffer_size
		self.window_size = window_size
		self.packet_size = packet_size
		self.timeoutval = timeoutval
		self.max_retransmits = max_retransmits
		self.send_head = self.send_base + self.window_size - 1

	def connect(self,target_host,port,request):
		syn_pac = Packet(1,0,0,0,0,bytes("First Packet", 'utf-8'))
		self.send(syn_pac,target_host,port)
		print("Client Connection Request Sent")
		ack = ""
		while(True):
			time.sleep(0.5)
			ack = self.recv(target_host,port)
			if ack is not None:
				break
			else:
				self.send(syn_pac,target_host,port)
				continue
		if(ack.split("~")[1]=="1" and ack.split("~")[3]=="1"):
			print("Server Connection ACK received")
			req_pac = Packet(1,0,0,0,0,bytes(request, 'utf-8'))  # SYN is 1 here..
			self.send(req_pac,target_host,port)
			print("File Request Sent")
		return

	def listen(self,target_host,port):
		conn_req = self.recv(target_host,port)
		if(conn_req.split("~")[1]=="1" and conn_req.split("~")[4]=="0"):
			print("Client Connection request received")
			req_pac = ""
			while(True):
				ack_pac = Packet(1,0,1,0,0,bytes("ACK Packet", 'utf-8'))
				self.send(ack_pac,target_host,port)
				print("Server connection ACK sent")
				time.sleep(0.5)
				req_pac = self.recv(target_host,port)
				if req_pac is not None:
					print(f"Client File request received:")
					break
				else:
					continue
			print(f"File name requested by client is {req_pac.split('~')[8]}")
			return req_pac.split("~")[8]
		return 0

	def send(self,packet,target_host,port):
		packet_params = packet.packet.split('~')
		pno = packet_params[4]
		# packet_bytes = packet.packet.encode("ascii")
		# base64_bytes = base64.b64encode(packet_bytes)
		# base64_string = base64_bytes.decode("ascii")
		self.s.sendto(bytes(packet.packet, encoding="utf-8"),(str(target_host),int(port)))
		if(packet_params[3]=="0" and packet_params[1]!="1"):
			print(f"Sent packet {pno}")
		elif(packet_params[3]=="1" and packet_params[1]!="1"):
			print(f"Sent ACK {packet_params[5]}")

	def bind(self,target_host,port):
		self.s.bind((str(target_host),int(port)))

	def recv(self,target_host,port):
		chunk,addr = self.s.recvfrom(self.packet_size)
		chunk = chunk.decode(encoding='utf-8')
		# base64_string = str(chunk)
		# base64_bytes = chunk.decode("ascii")
		# ascii_string_bytes = base64.b64decode(chunk)
		# recvd_string = ascii_string_bytes.decode("ascii")
		# packet_params = recvd_string.split('~')
		chunk = str(chunk)
		packet_params = chunk.split("~")
		pno = packet_params[4]
		checksum = packet_params[7]
		if(self.verifyChecksum(chunk,packet_params[7])==False):
			print(f"Packet {pno} compromised")
			return None
		elif(packet_params[1]=="0" and packet_params[2]=="0" and packet_params[3]=="0"):  # and packet_params[4]!="4" Add packet number here to check for packet loss
			print(f"Packet {pno} ok")
			ack_pack = Packet(0,0,1,0,pno,bytes("ACK Packet", 'utf-8'))
			self.send(ack_pack,target_host,port)
		return chunk


	def settimeout(self):
		self.s.settimeout(self.timeoutval)

	def close(self):
		self.s.close()

	def verifyChecksum(self,packet,chk):
		packet_params = packet.split("~")
		temp = ""
		temp += packet_params[0]
		temp += "~"
		temp += packet_params[1]
		temp += "~"
		temp += packet_params[2]
		temp += "~"
		temp += packet_params[3]
		temp += "~"
		temp += packet_params[4]
		temp += "~"
		temp += packet_params[5]
		temp += "~"
		temp += packet_params[6]
		temp += "~"
		temp += (packet_params[8])
		cc =  (((mmh3.hash(temp))) % (1<<16))
		print(cc)
		print(chk)
		if(int(cc)==int(chk)):
			return True
		else:
			return False


class Packet:
	payload = ""
	header = "1~"
	packet = ""
	SYN = 0
	FIN = 0
	ACK = 0
	PNO = 0
	ANO = 0
	body_length = 0
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
		self.body_length = len(payload)
		self.header += str(self.body_length)
		self.header += "~"
		self.checksum = self.computeChecksum()
		self.header += str(self.checksum)
		self.header += "~"
		self.packet += self.header
		#temp = self.payload.encode('ascii')
		#temp = self.payload.decode('ascii')
		self.packet += str(self.payload.decode(encoding='utf-8'))
		# self.packet += str(temp)
		# self.packet += self.payload
		# self.packet = bytes(self.packet, encoding="utf-8")

	def printPacket(self):
		print(self.packet)

	def computeChecksum(self):
		temp = self.header + str(self.payload.decode('utf-8'))
		return (((mmh3.hash(temp))) % (1<<16))



#comcast --device lo0 --stop