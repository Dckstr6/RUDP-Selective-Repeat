import socket
import RUDP
import math
import time
import threading
class Server:

    target_host = ""
    target_port = 0
    self_host = ""
    self_port = 0
    total_packets = 0
    number_of_acked_packets = 0
    packet_size = 30
    body_size = 10
    last_sent_index = 0
    retransmission_counter = 4
    s = RUDP.Connection()
    ack_array = list()
    total_data = list()
    all_threads = list()
    sleep_time = 2

    def __init__(self,self_host,self_port,target_host,target_port):
        self.target_host = str(target_host)
        self.target_port = target_port
        self.self_host = str(self_host)
        self.self_port = self_port
        self.s.bind(self.self_host,self.self_port)
        file_name = self.s.listen(self.target_host,self.target_port)
        count = 0
        with open(file_name,"r") as file:
            self.total_data = [ch for ch in file.read()]
        self.total_packets = math.ceil(len(self.total_data)/(self.body_size))
        self.ack_array = [0 for i in range(self.total_packets)]

        thread_ack = threading.Thread(target=self.listen_for_ack,args=())
        thread_ack.start()

        for i in range(self.total_packets):
            tx = threading.Thread(target=self.send_this_packet,args=(i,))
            tx.start()
            self.all_threads.append(tx)

        for i in range(self.total_packets):
            self.all_threads[i].join()

        self.s.close()

    def send_this_packet(self,packet_no):
        while(True):
            packet_body = ""
            i = 0
            while(i<self.body_size and self.last_sent_index < len(self.total_data)):
                packet_body += str(self.total_data[self.last_sent_index])
                self.last_sent_index += 1
                i += 1
            sending_packet = RUDP.Packet(0,0,0,packet_no,0,packet_body)
            self.s.send(sending_packet,self.target_host,self.target_port)
            time.sleep(self.sleep_time)
            if(self.ack_array[packet_no]==1):
                break
            else:
                print(f"ACK for packet {packet_no} is not received, resending packet")
                self.s.send(sending_packet,self.target_host,self.target_port)
                continue
        return

    def listen_for_ack(self):
        while(self.number_of_acked_packets < self.total_packets):
            response = self.s.recv(self.target_host,self.target_port)
            if(response.split("~")[3]=="1"):
                ack_no = int(response.split("~")[5])
                print(f"Received ACK for packet {ack_no}")
                self.ack_array[ack_no] = 1
                self.number_of_acked_packets += 1
        return

if __name__ == '__main__':
    s1 = Server("127.0.0.1",65432,"127.0.0.1",65431)






# {
#     "bufLen": 20, 
#     "windowSize": 10, 
#     "globalTimer": 1000000,
#     "packetSize": 10024,
#     "reTransCount": 3,
#     "serverIpAddr": "127.0.0.1",
#     "serverPortNo": 50125,
#     "clientIpAddr": "127.0.0.1",
#     "clientPortNo": 50126,
#     "reqFileName": "Rushabh.mp4"
# }

# Gaurang Gupta2:17 PM
# body = self.data[packNum *
#                              self.bodySize: min(((packNum + 1) * self.bodySize), self.lenOfData)]