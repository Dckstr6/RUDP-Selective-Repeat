import socket
import RUDP
import math
import time
import threading
import os
import base64
class Server:
    mutex = threading.Lock()
    target_host = ""
    target_port = 0
    self_host = ""
    self_port = 0
    total_packets = 0
    number_of_acked_packets = 0
    last_received_time = 0
    packet_size = 300
    body_size = 200
    last_sent_index = 0
    retransmission_counter = 4
    ack_array = list()
    total_data = ""
    all_threads = list()
    sleep_time = 3
    window_size = 0
    send_head = 0
    send_base = 0
    serv_timeout = 0

    def __init__(self,self_host,self_port,target_host,target_port,retransmission_counter,window_size,sleep_time,serv_timeout=30,packet_size=1500,body_size=1000):
        self.target_host = str(target_host)
        self.target_port = target_port
        self.self_host = str(self_host)
        self.self_port = self_port
        self.retransmission_counter = retransmission_counter
        self.window_size = window_size
        self.send_head = self.send_base + self.window_size - 1
        self.sleep_time = sleep_time
        self.serv_timeout = serv_timeout
        self.packet_size = packet_size
        self.body_size = body_size
        self.s = RUDP.Connection(timeoutval=self.serv_timeout)

        self.s.bind(self.self_host,self.self_port)
        file_name = self.s.listen(self.target_host,self.target_port)
        count = 0
        with open(file_name,"rb") as file:
            self.total_data = file.read()
            self.total_data = base64.encodebytes(self.total_data)
        self.total_packets = math.ceil(len(self.total_data)/(self.body_size))
        print(f"Total packets are {self.total_packets}")
        for i in range(0,self.total_packets):
            self.ack_array.append(0)
        thread_ack = threading.Thread(target=self.listen_for_ack,args=())
        thread_ack.start()
        self.last_received_time = time.time()
        thread_timer = threading.Thread(target=self.global_timer,args=())
        thread_timer.start()
        for i in range(self.total_packets):
            tx = threading.Thread(target=self.send_this_packet,args=(i,))
            tx.start()
            self.all_threads.append(tx)

        for i in range(self.total_packets):
            self.all_threads[i].join()
        thread_ack.join()

        self.end_connection()
        self.s.close()
        os._exit(0)


    def send_this_packet(self,packet_no):
        retries = 0
        flag = 0
        while(flag==0):
            if(packet_no >= self.send_base and packet_no <= self.send_head):
                print(f"Able to send packet {packet_no}")
                flag = 1
                while(True):
                    packet_body = ""
                    packet_body = self.total_data[(self.body_size*packet_no):min(self.body_size*(packet_no+1),len(self.total_data))]
                    # for i in range((self.body_size*packet_no),min(self.body_size*(packet_no+1),len(self.total_data))):
                    #     packet_body += str(self.total_data[i])
                    sending_packet = RUDP.Packet(0,0,0,packet_no,0,packet_body)
                    self.s.send(sending_packet,self.target_host,self.target_port)
                    time.sleep(self.sleep_time)
                    if(self.ack_array[packet_no]==1):
                        break
                    elif(retries < self.s.max_retransmits):
                        print(f"ACK for packet {packet_no} is not received, resending packet again ({retries})")
                        retries += 1
                        self.s.send(sending_packet,self.target_host,self.target_port)
                        continue
                    else:
                        print("Exceeded maximum retransmits, terminating connection......")
                        self.end_connection()
                        os._exit(0)
                break
            else:
                continue
        return

    def listen_for_ack(self):
        while(self.number_of_acked_packets < self.total_packets):
            response = self.s.recv(self.target_host,self.target_port)
            if(response.packet.split("~")[3]=="1"):
                ack_no = int(response.packet.split("~")[5])
                print(f"Received ACK for packet {ack_no}")
                self.mutex.acquire()
                if(self.ack_array[ack_no]==0):
                    self.ack_array[ack_no] = 1
                    self.number_of_acked_packets += 1
                self.last_received_time = time.time()
                self.mutex.release()
                if((self.ack_array[self.send_base]==1)):
                    self.mutex.acquire()
                    try:
                        if((self.send_base < self.total_packets - self.window_size)):
                            self.send_base += 1
                            self.send_head += 1
                            print(f"Send base is now {self.send_base}")
                            print(f"Send head is now {self.send_head}")
                    finally:
                        self.mutex.release()
        print("All ACKS Received. Initiating termination")
        return

    def global_timer(self):
        while(True):
            if(time.time() - self.last_received_time) >= self.s.timeoutval:
                print(f"Timeoutval is {self.s.timeoutval}")
                print(f"Time.Time is {time.time()}")
                print(f"Last Received Time is {self.last_received_time}")
                print("Global Timer exceeded")
                os._exit(0)

    def end_connection(self):
        fin_packet = RUDP.Packet(0,1,0,0,0,bytes("End Connection", 'utf-8'))
        self.s.send(fin_packet,self.target_host,self.target_port)
        print("Server ending connection")
        return

if __name__ == '__main__':
    s1 = Server("127.0.0.1",65432,"127.0.0.1",65431,5,3,3)






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