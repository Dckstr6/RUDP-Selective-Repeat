import socket
import threading
from _thread import *
from socketserver import ThreadingMixIn
import base64
import mmh3
import time
import os

## Used to create a connection, transfer data between server and client
#
#  Creates a udp connection with reliability between the server and the client.
#
#  Starts with a 3 way handshake and then the file trnasfer starts
#  It checks for acknowledgement for each packet sent
#  After a time of 3 seconds, if an ack for a packet is still not received, then the packet is sent again
#  This can take place for a maximum of 5 times or maximum time of 30s (default values), whichever comes first
#  
class Connection:
	## max no of retransmits
	max_retransmits = 0
	## packet size
	packet_size = 0
	## socket
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	## timeout value
	timeoutval = 0

	# Problem is due to this packet size in client.

	## Class constructor
	# 
	#  @param self The object pointer
	#  @param packet_size packet size
	#  @param max_retransmits max no of retransmits
	def __init__(self,packet_size=10024,timeoutval=30,max_retransmits = 5):
		self.packet_size = packet_size
		self.timeoutval = timeoutval
		self.max_retransmits = max_retransmits

	## connect client to server
	# 
	#  Used to connect client to the server.
	#  Three way handshake is implemented here
	#  @param self The object pointer
	#  @param target_host server ip
	#  @param port server port
	#  @param request requested file name
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
		if(ack.packet.split("~")[1]=="1" and ack.packet.split("~")[3]=="1"):
			print("Server Connection ACK received")
			req_pac = Packet(1,0,0,0,0,bytes(request, 'utf-8'))  # SYN is 1 here..
			self.send(req_pac,target_host,port)
			print("File Request Sent")
		return

	## Listen to connection requests
	#
	#  Used to listen for connection requests. Three way handshake implemented
	#  Calls the function to send the file before exitting
	#  @param self The object pointer
	#  @param target_host client ip
	#  @param port client port
	def listen(self,target_host,port):
		conn_req = self.recv(target_host,port)
		if(conn_req.packet.split("~")[1]=="1" and conn_req.packet.split("~")[4]=="0"):
			print("Client Connection request received")
			req_pac = ""
			while(True):
				ack_pac = Packet(1,0,1,0,0,bytes("ACK Packet", 'utf-8'))
				self.send(ack_pac,target_host,port)
				print("Server connection ACK sent")
				time.sleep(0.5)
				req_pac = self.recv(target_host,port)
				if req_pac is not None:
					print(f"Client File request received")
					break
				else:
					continue
			print(f"File name requested by client is {req_pac.packet.split('~')[8]}")
			return req_pac.packet.split("~")[8]
		return 0

	## Send packet to client or send acknowledgement to server
	#
	#  send the requested file to the client
	#  uses utf-8 encoding 
	#  @param packet a Packet @see Packet Class
	#  @param target_host server/client ip
	#  @param port server/client port
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

	## Bind server/client
	#
	#  @param self The object pointer
	#  @param target_host server/client ip
	#  @param port server/client port
	def bind(self,target_host,port):
		self.s.bind((str(target_host),int(port)))

	## Receive packet from server
	#
	#  Receive packet from server and send acknowledgement
	#  Verifies if packet is not damaged
	#  @param self The object pointer
	#  @param target_host server ip
	#  @param port server port
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
		recvd_packet = Packet(packet_params[1],packet_params[2],packet_params[3],packet_params[4],packet_params[5],bytes(packet_params[8],'utf-8'))
		return recvd_packet

	## Close socket
	#
	#  @param self The object pointer
	def close(self):
		self.s.close()

	## Verify if packet is not damaged
	#
	#  @param self The object pointer
	#  @param packet a Packet @see Packet Class
	#  @param chk an integer to check if packet is not damaged
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
		temp += packet_params[8]
		cc =  (((mmh3.hash(temp))) % (1<<16))
		print(cc)
		print(chk)
		if(int(cc)==int(chk)):
			return True
		else:
			return False


## Packet Class: Used to store some information about the 
#
#  Contains headers and body. Headers ensure the packet has safely reached. Body contains a part of the information to be sent
class Packet:
	## payload of the packet
	payload = b""
	## header of the packet
	header = "1~"
	## packet body
	packet = ""
	## SYN bit
	SYN = 0
	## FIN bit
	FIN = 0
	## ACK bit
	ACK = 0
	## PNO bit
	PNO = 0
	## ANO bit
	ANO = 0
	## body size
	body_length = 0
	## check sum value
	checksum = ""


	## Class constructor
	#  
	#  Assembles the body and header of the packet
	#  @param self The object pointer
	#  @param SYN the SYN bit
	#  @param FIN the FIN bit
	#  @param ACK the ACK bit
	#  @param PNO the PNO bit
	#  @param ANO the ANO bit
	#  @param payload the payload of the packet
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
		temp_str = str(self.payload.decode(encoding='utf-8'))
		self.body_length = len(temp_str)
		self.header += str(self.body_length)
		self.header += "~"
		self.checksum = self.computeChecksum()
		self.header += str(self.checksum)
		self.header += "~"
		self.packet += self.header
		self.packet += temp_str



	## print packet
	def printPacket(self):
		print(self.packet)

	## computes checksum value after decoding the packet
	def computeChecksum(self):
		temp = self.header + str(self.payload.decode(encoding='utf-8'))
		return (((mmh3.hash(temp))) % (1<<16))



#comcast --device lo0 --stop



