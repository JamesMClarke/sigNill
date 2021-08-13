import socket
import threading
import sys


#TODO add threading, to allow for multiple clients 
#TODO convert to p2p
#TODO start each message with username
#TODO if ip address is already in used use another
#TODO add error handling if client dc's from server

class Server:

    connections = []

    def __init__(self):
        
        #creates TCP socket
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_ip = '127.0.0.1'
        #port 60 unassigned
        tcp_port = 8080

        #recieving data bugger
        self.buf_size = 30
        self.tcp_sock.bind((tcp_ip,tcp_port))
        self.tcp_sock.listen(1)
        
        self.con, addr = self.tcp_sock.accept()
        print("connection address is :", addr)

    def handler(self,c,a):

        while True:
            data = c.recv(self.buf_size)
            for connection in self.connections: 
                connection.send(data)

            if not data:
                #to do get user name 
                print("disconnected")
                break
            print("recieved data", data)
                #con.close   
            self.con.send(data)

    def run(self):
        while True:
            c,a = self.tcp_sock.accept()
            connect_thread = threading.Thread(target=self.handler,args = (c,a))
            connect_thread.daemon =True
            connect_thread.start()
            self.connections.append(c)









class Client:

    def __init__(self):
        tcp_port = 8080
        tcp_ip = '127.0.0.1'
        buff_size = 1024


        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((tcp_ip,tcp_port))

        input_thread = threading.Thread(target=self.send_mesg)
        input_thread.daemon = True
        input_thread.start()

        while True:
            data = self.tcp_sock.recv(buff_size)
            print(data)
            if not data:
                break




        data = self.tcp_sock.recv(buff_size)
        print(data)

        


    def send_mesg(self):
        while True:

            mesg = input()

            self.tcp_sock.send(mesg.encode('utf-8'))
            if(mesg =='exit'):
                self.tcp_sock.close()

        



if (len(sys.argv)>1):
    client = Client()
else:
    server = Server()
    server.run()




