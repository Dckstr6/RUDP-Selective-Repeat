import socket
import RUDP
import os
import threading
import time
from collections import OrderedDict
import base64
import timeit

class Client:
    request = ""
    target_host = ""
    target_port = 0
    self_host = ""
    self_port = 0
    packet_size = 0
    body_size =0 
    packet_list = {}
    last_received_time = 0
    start_time = time.time()
    write_list = b""
    cl_timeout = 0
    def __init__(self,self_host,self_port,target_host,target_port,file_request,cl_timeout=30,packet_size=10024,body_size=8000):
        start = timeit.default_timer()
        self.target_host = str(target_host)
        self.target_port = target_port
        self.self_host = str(self_host)
        self.self_port = self_port
        self.request = str(file_request)
        self.cl_timeout = cl_timeout
        self.packet_size = packet_size
        self.body_size = body_size
        self.s = RUDP.Connection(timeoutval=cl_timeout,packet_size=self.packet_size)

        self.s.bind(self.self_host,self.self_port)
        self.s.connect(self.target_host,self.target_port,self.request)
        self.last_received_time = time.time()
        elapsed_thread = threading.Thread(target=self.time_elapsed,args=())
        elapsed_thread.start()
        thread_timer = threading.Thread(target=self.global_timer,args=())
        thread_timer.start()
        while(True):
            line = self.s.recv(target_host,target_port)
            if(line is not None):
                self.last_received_time = time.time()
                if(line.packet.split("~")[2]=="1"):
                    print("Server closing connection")
                    break
                pno = int(line.packet.split("~")[4])
                temp = line.payload
                self.packet_list[pno] = temp
        self.s.close()
        # print(self.packet_list)
        od = OrderedDict(sorted(self.packet_list.items()))
        for no,body in od.items():
            self.write_list += body
        # print((base64.decodebytes(self.write_list)).decode())
        output_file = "output."
        temp = file_request.split(".")
        output_file += temp[1]
        # final_write_list = final_write_list.decode('ascii')
        # print(self.write_list)
        with open(output_file,"wb") as f:
            final = (base64.decodebytes(self.write_list))
            f.write(final)

        print(f"Written to {output_file}")
        stop = timeit.default_timer()
        f = open("times.txt", "a")
        k = stop - start
        s = str(k)
        f.write(s + '\n')
        f.close()
        os._exit(0)


    def global_timer(self):
        while(True):
            if(time.time() - self.last_received_time) >= self.s.timeoutval:
                print(f"Timeoutval is {self.s.timeoutval}")
                print(f"Time.Time is {time.time()}")
                print(f"Last Received Time is {self.last_received_time}")
                print("Global Timer exceeded")
                os._exit(0)

    def check_contiguous(self):
        while(True):
            return
    
    def time_elapsed(self):
        current_time = time.time()
        elap = current_time - self.start_time
        return elap


if __name__ == '__main__':
    c1 = Client("127.0.0.1",65431,"127.0.0.1",65432,"sample.png")

