import socket
import RUDP

class Client:
    def __init__(self):
        request = "sample.txt"
        message = "abcd"

        s = RUDP.Connection()
        s.bind("127.0.0.1",65431)
        s.connect("127.0.0.1",65432,request)
        while(True):
            line = s.recv()
            print(line)
        s.close()
