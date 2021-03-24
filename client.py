import socket
import RUDP


request = "sample.txt"
message = "abcd"

s = RUDP.Connection()
count = 0
with open('sample.txt','r') as file:
    for line in file:
        p = RUDP.Packet(0,0,0,count,0,line)
        s.send(p,"127.0.0.1",65432)
        count += 1



s.close()