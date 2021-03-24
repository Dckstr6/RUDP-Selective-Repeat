import socket
import RUDP

class ClientConnection:

    request = "sample.txt"
    message = "abcd"
    serverip = "127.0.0.1"
    serverport = 65432
    def __init__(self, request = "sample.txt", message = "abcd", serverip = "127.0.0.1", serverport = 65432) :
        self.request = request
        self.message = message
        self.serverip = serverip
        self.serverport = serverport
    def connect(self):
        s = RUDP.Connection()
        count = 0
        with open(self.request,'r') as file:
            for line in file:
                p = RUDP.Packet(0,0,0,count,0,line)
                s.send(p,self.serverip,self.serverport)
                count += 1

        s.close()