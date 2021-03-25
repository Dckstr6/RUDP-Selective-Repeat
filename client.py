import socket
import RUDP


class Client:
    body_parts = {}
    request = ""
    target_host = ""
    target_port = 0
    self_host = ""
    self_port = 0
    s = RUDP.Connection()

    def __init__(self,self_host,self_port,target_host,target_port,file_request):
        self.target_host = str(target_host)
        self.target_port = target_port
        self.self_host = str(self_host)
        self.self_port = self_port
        self.request = str(file_request)
        self.s.bind(self.self_host,self.self_port)
        self.s.connect(self.target_host,self.target_port,self.request)
        while(True):
            line = self.s.recv(target_host,target_port)
            pno = int(line.split("~")[4])
            body = line.split("~")[8]
            print(f"Body recevied in packet {pno}: {body}")
        self.s.close()


if __name__ == '__main__':
    c1 = Client("127.0.0.1",65431,"127.0.0.1",65432,"sample.txt")



# request = "sample.txt"
# message = "abcd"

# s = RUDP.Connection()
# s.bind("127.0.0.1",65431)
# s.connect("127.0.0.1",65432,request)
# while(True):
#     line = s.recv()
#     print(line)
# s.close()
