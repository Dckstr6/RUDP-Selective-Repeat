import socket

class Connection:
	buffer_size = 0
	window_size = 0
	packet_size = 0
	packet = NULL
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

	def __init__(self,buffer_size,window_size,packet_size,packet):
		self.buffer_size = buffer_size
		self.window_size = window_size
		self.packet_size = packet_size
		self.packet = packet

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
		print(packet)

if __name__ == '__main__':
	p = Packet(1,1,1,1,1,"abcd")
	p.printPacket()