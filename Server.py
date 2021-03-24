import socket
import RUDP


class ServerConnection:
    serverip = "127.0.0.1"
    port = 65432
    def __init__(self, serverip = "127.0.0.1", port = 65432):
        self.serverip =  str(serverip)
        self.port = port
    def connect(self):
        s = RUDP.Connection()
        s.bind(self.serverip,self.port)
        s.recv()
        s.close()
