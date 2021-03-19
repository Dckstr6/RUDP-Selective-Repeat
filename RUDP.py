import socket

class Connection:
	buffer_size = 0
	window_size = 0
	packet_size = 0
	packet = 0
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	target_host = 0
	timeoutval = 0
	fragments = list()
	port = 0

	def __init__(self,buffer_size,window_size,packet_size,packet,target_host,port,timeoutval):
		self.buffer_size = buffer_size
		self.window_size = window_size
		self.packet_size = packet_size
		self.packet = packet
		self.target_host = target_host
		self.port = port
		self.timeoutval = timeoutval

	def connect(self):
		self.s.connect((str(self.target_host),int(self.port)))

	def send(self):
		msglen = len(self.packet)
		self.s.sendto(self.packet,(self.target_host,self.port))

	def recv(self):
		while True:
			chunk,addr = self.s.recvfrom(65535)
			if not chunk:
				break
			fragments.append(chunk)

	def settimeout(self):




class Packet:
	payload = ""
	header = "1"
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
		self.header += str(FIN)
		self.header += str(ACK)
		self.header += str(PNO)
		self.header += str(ANO)
		self.payload = payload
		self.packet += self.header
		self.packet += "\r\n\r\n"
		self.packet += self.payload

	def printPacket(self):
		print(self.packet)

if __name__ == '__main__':
	p = Packet(1,1,1,1,1,"abcd")
	p.printPacket()