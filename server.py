import socket

fragments = list()
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(("127.0.0.1",65432))
s.settimeout(10)

while True:
    try:
        chunk,addr = s.recvfrom(1024)
    except socket.timeout:
        print("Socket timeout")
        break
    print(f"Recvd {chunk.decode('utf-8')}")
    if not chunk:
        break
    fragments.append(chunk)

print(fragments)