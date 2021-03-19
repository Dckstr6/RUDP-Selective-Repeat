import socket

fragments = list()
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(("127.0.0.1",65432))
s.settimeout(2)

while True:
    try:
        chunk,addr = s.recvfrom()
    except socket.timeout:
        print("Socket timedout")
    print(f"Recvd {chunk}")
    if not chunk:
        break
    fragments.append(chunk)

print(fragments)