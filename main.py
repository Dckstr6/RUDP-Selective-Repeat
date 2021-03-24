import sys
import Server
import Client

def startServer():
    print("Starting server")
    server = ""
    if len(sys.argv)>=4:
        server = Server.ServerConnection(sys.argv[2], sys.argv[3])
    else:
        server = Server.ServerConnection()
    print("Server started")
    server.connect()

def startClient():
    print('Client Starting')
    client = ''
    if len(sys.argv) == 6:
        client = Client.ClientConnection(sys.argv[5], sys.argv[6])
    else:
        client = Client.ClientConnection()
    print('Client Started')
    client.connect()


if sys.argv[1] == '0':
    startServer()
else:
    startClient()