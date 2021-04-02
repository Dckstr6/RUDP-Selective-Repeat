import socket
import RUDP
import os
import threading
import time
from collections import OrderedDict

class Client:
    request = ""
    target_host = ""
    target_port = 0
    self_host = ""
    self_port = 0
    s = RUDP.Connection()
    # Change packet list from list to dict
    packet_list = {}
    last_received_time = 0
    write_list = list()
    def __init__(self,self_host,self_port,target_host,target_port,file_request):
        self.target_host = str(target_host)
        self.target_port = target_port
        self.self_host = str(self_host)
        self.self_port = self_port
        self.request = str(file_request)
        self.s.bind(self.self_host,self.self_port)
        self.s.connect(self.target_host,self.target_port,self.request)
        # thread_timer = threading.Thread(target=self.global_timer,args=())
        # thread_timer.start()
        while(True):
            line = self.s.recv(target_host,target_port)
            if(line is not None):
                self.last_received_time = time.time()
            if(line.split("~")[2]=="1"):
                print("Server closing connection")
                break
            pno = int(line.split("~")[4])
            body = line.split("~")[8]
            print(f"Body received in packet {pno}: {body}")
            self.packet_list[pno] = body
        self.s.close()
        # print(self.packet_list)
        od = OrderedDict(sorted(self.packet_list.items()))
        for no,body in od.items():
            for word in body:
                self.write_list.append(word)
        # print(self.write_list)
        with open("output.txt","w") as f:
            for letter in self.write_list:
                f.write(letter)

        os._exit(0)


    def global_timer(self):
        while(True):
            if(time.time() - self.last_received_time) >= self.s.timeoutval:
                print(f"Timeoutval is {self.s.timeoutval}")
                print("Global Timer exceeded")
                os._exit(0)


if __name__ == '__main__':
    c1 = Client("127.0.0.1",65431,"127.0.0.1",65432,"sample.txt")

