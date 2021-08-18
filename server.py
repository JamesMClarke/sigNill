import json as js
from os import error
from users import Users
import socket,errno
import threading
import sys

#TODO add kick client option
#TODO add server status log

class Server:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    users = Users()

    def __init__(self):

        #server run method is ran on sperate thread 
        run_thread = threading.Thread(target=self.run)
        run_thread.daemon = True
        run_thread.start()

        #server menu is ran on main thread
        self.menu()
    

    def handler(self,c,a):

        username = ""
        message = ""
        while True:
            #loads data json object sent by client
            data = c.recv(self.buf_size)
            print(data)
            data = js.loads(data)
                
            # if key username in data, adds connecting client username and ip address to users array
            if("username" in data):
                username = data["username"]
                self.users.add_user(username, c)
                print(username,str(a[0])+":"+str(a[1]),"connected")
            
            #direct messaging if keys target and message in data retrieves target ip by searching for username
            if all(key in data for key in ("target","message")):
                username_to_find = str(data["target"])
                message = str(data["message"])
                print(username_to_find)
                target_ip = self.users.find_conn_by_name(username_to_find)

                #if target_ip not null senders name and message is sent to recipent
                if(target_ip != None):
                    #create json object with username of sender and message so that the recpent knows who sent the message
                    data_to_send = js.dumps({"username":username,"message":message})
                    data = js.dumps(data)
                    target_ip.send(bytes(data_to_send,encoding='utf-8'))

            # if no data connection lost client connection closed close
            if not data:
                #displays disconnected client
                print(str(username),"disconnected")
                self.connections.remove(c)
                c.close()
                break
    #server menu
    def menu(self):
        print("\nCommands: \n1: List all clients\n0: Exit")       
        while True:
            i = input()
        
                
            if (i== "0"):
                self.tcp_sock.close()
                print("server closed") 
                sys.exit()

            #Lists all clients
            #TODO: Fix showing "User: 0"
            #TODO: Add the rest of the connection info by returning 2d array from get_connections()
            elif(i == "1"):
                users = self.users.get_all_usernames()
                for name in users:
                    print("User: "+str(name)) 
            else:
                print("not valid command")

    #initializes server
    def run(self):

        #assigns server TCP ip, Port and recieving data buffer size
        tcp_ip = '127.0.0.1'
        tcp_port = 8080
        self.buf_size = 128
        
        #binds tcp socket and listens on it
        #if port in use, alt port num is used
        try :
            self.tcp_sock.bind((tcp_ip,tcp_port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("port "+ str(tcp_port)+" in use, using alternative port")
                tcp_port = 10080
                self.tcp_sock.bind((tcp_ip,tcp_port))

        self.tcp_sock.listen(1)
        print('server running')

        while True:
            #accepts incoming connect requests 
            c,a = self.tcp_sock.accept()

            #creates new client handler thread for each connected client
            handler_thread = threading.Thread(target=self.handler,args = (c,a))
            handler_thread.daemon =True
            handler_thread.start() 
            
        


        




server = Server()




