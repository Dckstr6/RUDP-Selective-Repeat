import socket

message = b"abcd"

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

for i in range(10):
    s.sendto(message,("127.0.0.1",65432))
s.close()