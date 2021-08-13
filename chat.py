import socket
import threading
import sys


#TODO add threading, to allow for multiple clients
#TODO convert to p2p
#TODO start each message with username

class Server:

    def __init__(self):
        
        #creates TCP socket
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_ip = '127.0.0.1'
        #port 60 unassigned
        tcp_port = 8080

        #recieving data bugger
        buf_size = 30
        tcp_sock.bind((tcp_ip,tcp_port))
        tcp_sock.listen(1)
        
        con, addr = tcp_sock.accept()
        print("connection address is :", addr)

        while True:
            data = con.recv(buf_size)

            if not data:
                break
            print("recieved data", data)
            con.send(data)
            con.close









class Client:

    def __init__(self) -> None:
        tcp_port = 8080
        tcp_ip = '127.0.0.1'
        buff_size = 1024


        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((tcp_ip,tcp_port))

        mesg = input()


        tcp_sock.send(mesg.encode('utf-8'))

        data = tcp_sock.recv(buff_size)
        print(data)

        #closes socket
        
        tcp_sock.close()


if (len(sys.argv)>1):
    client = Client()
else:
    server = Server()




