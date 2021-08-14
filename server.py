import socket
import threading
import sys


#TODO convert to p2p
#TODO start each message with username
#TODO if port is already in used use another
#TODO add encypt message
#TODO rename file to signill, allow args for server and client mode
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
                #displays disconnected client
                print(str(a[0])+ str(a[1]),"disconnected")
                self.connections.remove(c)
                c.close()

                break
            print("recieved data", data)
    
    def menu(self):
        i = input("Input")
        print(i)
        if(i == "exit"):
            self.tcp_sock.close()
            quit()

    def run(self):
        while True:
            
            c,a = self.tcp_sock.accept()
            connect_thread = threading.Thread(target=self.handler,args = (c,a))
            connect_thread.daemon =True
            connect_thread.start()
            
            menu_thread = threading.Thread(target=self.menu)
            menu_thread.daemon = True
            menu_thread.start()
            

            self.connections.append(c)
            print(str(a[0])+":"+str(a[1]),"connected")


        




server = Server()
server.run()




