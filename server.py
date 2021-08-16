import json as js
import socket
import threading
import sys


#TODO start each message with username
#TODO if port is already in used use another
#TODO add encypt message
#TODO add kick client option
#TODO allow for mesg to be sent to designated client -SC

class Server:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connections = [[0 for i in range(3)] for j in range(10)]
    connections = []

    def __init__(self):

        
        run_thread = threading.Thread(target=self.run)
        run_thread.daemon = True
        run_thread.start()
        
        self.menu()
    
        #self.con, addr = self.tcp_sock.accept()

    def handler(self,c,a):

        while True:
            
            data = c.recv(self.buf_size)

            for connection in self.connections: 
                connection[0].send(data)    

            if not data:
                #displays disconnected client
                print(str(a[0])+ str(a[1]),"disconnected")
                self.connections.remove(c)
                c.close()

                break
    
    def menu(self):
        
        i = input("Input: ")
    
            
        if (i== "exit"):
            self.tcp_sock.close()
            print("server closed") 
            sys.exit()

        if(i == "list-clients"):
            for connection in self.connections:
                print(connection)
            if(len(self.connections) == 0):
                print("no connections")

        if(i== "help"):
            print("Available Commands:\nlist-clients\nexit\nhelp")
            
        else:
            print("not valid command")
        self.menu()


    def run(self):

        
        #creates TCP socket, assigns ip,port
        tcp_ip = '127.0.0.1'
        tcp_port = 8080

        #recieving data bugger
        self.buf_size = 30
        self.tcp_sock.bind((tcp_ip,tcp_port))
        self.tcp_sock.listen(1)
        print('server running\n')


        while True:
            
            c,a = self.tcp_sock.accept()
            connect_thread = threading.Thread(target=self.handler,args = (c,a))
            connect_thread.daemon =True
            connect_thread.start() 
            
            self.connections.append(c)

            #data = 'client connected'
            #c.send(bytes(data,encoding ='utf-8'))

            print("\n",str(a[0])+":"+str(a[1]),"connected")


        




server = Server()




