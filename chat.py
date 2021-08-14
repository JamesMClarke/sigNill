import socket
import threading
import sys


#TODO convert to p2p
#TODO start each message with username
#TODO if port is already in used use another
#TODO add error handling if client dc's from server
#TODO BUG: investigate second client having to restart to send messages

class Server:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []

    def __init__(self):
        
        #creates TCP socket, assigns ip,port
        tcp_ip = '127.0.0.1'
        tcp_port = 8080

        #recieving data bugger
        self.buf_size = 30
        self.tcp_sock.bind((tcp_ip,tcp_port))
        self.tcp_sock.listen(1)
        print('server running')
        
        #self.con, addr = self.tcp_sock.accept()

    def handler(self,c,a):

        while True:
            
            data = c.recv(self.buf_size)
            for connection in self.connections: 
                connection.send(data)

            if not data:
                #to do get user name 
                print(str(a[0])+ str(a[1]),"disconnected")
                self.connections.remove(c)
                c.close()

                break
            print("recieved data", data)

    def run(self):
        while True:
            
            c,a = self.tcp_sock.accept()
            connect_thread = threading.Thread(target=self.handler,args = (c,a))
            connect_thread.daemon =True
            connect_thread.start()
            
            self.connections.append(c)
            print(str(a[0])+":"+str(a[1]),"connected")





class Client:
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def __init__(self):
        tcp_port = 8080
        tcp_ip = '127.0.0.1'
        buff_size = 1024


        self.tcp_sock.connect((tcp_ip,tcp_port))
        

        input_thread = threading.Thread(target=self.send_mesg)
        input_thread.daemon = True
        input_thread.start()

        while True:
            data = self.tcp_sock.recv(buff_size)
            print(data)
            if not data:
                break
            print(str(data,'utf-8'))


        


    def send_mesg(self):
      
        while True:
            
            mesg = input()
            self.tcp_sock.send(bytes(mesg,'utf-8'))
            if( mesg =='exit'):
                self.tcp_sock.close()
                exit()

        



if (len(sys.argv)>1):
    client = Client()
else:
    server = Server()
    server.run()




