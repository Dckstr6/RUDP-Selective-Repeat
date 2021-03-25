import socket
import threading
from _thread import *
from socketserver import ThreadingMixIn
import base64
import mmh3

class Connection:
	buffer_size = 0
	window_size = 3
	seq_space = 6
	packet_size = 65535
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	timeoutval = 0

	def __init__(self,buffer_size=0,window_size=0,packet_size=1024,timeoutval=0):
		self.buffer_size = buffer_size
		self.window_size = window_size
		self.packet_size = packet_size
		self.timeoutval = timeoutval

	def connect(self,target_host,port,request):
		syn_pac = Packet(1,0,0,0,0,"")
		self.send(syn_pac,target_host,port)
		print("Client Connection Request Sent")
		ack = self.recv(target_host,port)
		if(ack.split("~")[1]=="1" and ack.split("~")[3]=="1"):
			print("Server Connection ACK received")
			req_pac = Packet(1,0,0,0,0,str(request))
			self.send(req_pac,target_host,port)
			print("File Request Sent")
		return

	def listen(self,target_host,port):
		conn_req = self.recv(target_host,port)
		if(conn_req.split("~")[1]=="1" and conn_req.split("~")[4]=="0"):
			print("Client Connection request received")
			ack_pac = Packet(1,0,1,0,0,"")
			print("Server connection ACK sent")
			self.send(ack_pac,target_host,port)
			req_pac = self.recv(target_host,port)
			print(f"Client File request received:")
			print(f"File name requested by client is {req_pac.split('~')[8]}")
			return req_pac.split("~")[8]
		return 0

	def send(self,packet,target_host,port):
		packet_params = packet.packet.split('~')
		pno = packet_params[4]
		packet_bytes = packet.packet.encode("ascii")
		base64_bytes = base64.b64encode(packet_bytes)
		base64_string = base64_bytes.decode("ascii")
		self.s.sendto(base64_bytes,(str(target_host),int(port)))
		if(packet_params[3]=="0" and packet_params[1]!="1"):
			print(f"Sent packet {pno}")
		elif(packet_params[3]=="1" and packet_params[1]!="1"):
			print(f"Sent ACK {packet_params[5]}")

	def bind(self,target_host,port):
		self.s.bind((str(target_host),int(port)))

	def recv(self,target_host,port):
		chunk,addr = self.s.recvfrom(1024)
		base64_string = str(chunk)
		base64_bytes = chunk.decode("ascii")
		ascii_string_bytes = base64.b64decode(chunk)
		recvd_string = ascii_string_bytes.decode("ascii")
		packet_params = recvd_string.split('~')
		# print(f"Received string {recvd_string}")
		pno = packet_params[4]
		# print(f"Body is {packet_params[8]}")
		checksum = packet_params[7]
		if(self.verifyChecksum(packet_params[8],packet_params[7])==False):
			print(f"Packet {pno} compromised")
			return
		elif(packet_params[1]=="0" and packet_params[3]=="0"):
			print(f"Packet {pno} ok")
			ack_pack = Packet(0,0,1,0,pno,"")
			self.send(ack_pack,target_host,port)
		return recvd_string


	def settimeout(self):
		self.s.settimeout(self.timeoutval)

	def close(self):
		self.s.close()

	def verifyChecksum(self,body,chk):
		cc =  (((mmh3.hash(body))) % (1<<16))
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
		self.packet += self.payload

	def printPacket(self):
		print(self.packet)

	def computeChecksum(self):
		return (((mmh3.hash(self.payload))) % (1<<16))



# {
#     "bufLen": 20,
#     "windowSize": 10,
#     "globalTimer": 1000000,
#     "packetSize": 10024,
#     "reTransCount": 3,
#     "serverIpAddr": "127.0.0.1",
#     "serverPortNo": 50125,
#     "clientIpAddr": "127.0.0.1",
#     "clientPortNo": 50126,
#     "reqFileName": "Rushabh.mp4"
# }

# body_size = packet_size - 1024