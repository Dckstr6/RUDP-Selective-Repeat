import socket
import RUDP

class Server:
    s = RUDP.Connection()
    s.bind("127.0.0.1",65432)
    file_name = "sample.txt"
    file_name = s.listen("127.0.0.1",65431)

    count = 0
    with open(file_name,"r") as file:
        for line in file:
            p = RUDP.Packet(0,0,0,count,0,line)
            s.send(p,"127.0.0.1",65431)
            count += 1
    s.close()