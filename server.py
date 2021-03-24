import socket
import RUDP

s = RUDP.Connection()
s.bind("127.0.0.1",65432)

s.recv()
s.close()