from datetime import datetime
import json as js
from os import error
from users import Users
import socket, errno,threading, sys, logging

#TODO add kick client option
#TODO Add some type of userinput sanitization

logging.basicConfig(filename="logs/"+str(datetime.now())+".log", level=logging.DEBUG)

class Server:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    users = Users()

    def __init__(self):
        logging.debug("Server started at %s"%(datetime.now().strftime("%H:%m")))
        #server run method is ran on separate thread 
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
            logging.debug("Server receive %s at %s"%(data, datetime.now().strftime("%H:%m")))
            if(data):
                data = js.loads(data)
                            
                #direct messaging if keys target and message in data retrieves target ip by searching for username
                if ("target" in data):
                    target = str(data["target"])
                    
                    #Server commands
                    if(target == "server"):
                        if(data['status'] == "connected"):
                            #TODO Move this back to where it was above outside of the 2 if's
                            #This is due to the fact the user could be connected but no have the server see as such
                            #However, before adding the user to the list, it needs to be checked that a user does not already have the same name
                            username = data["sender"]
                            self.users.add_user(username, c)
                            logging.debug("User '%s', '%s' , '%s' connected at %s"%(username,str(a[0]),str(a[1]), datetime.now().strftime("%H:%m")))

                    else:
                    
                        target_ip = self.users.find_conn_by_name(target)

                        #if target_ip not null senders name and message is sent to recipent
                        if(target_ip != None):
                            #create json object with username of sender and message so that the recpent knows who sent the message
                            data = js.dumps(data)
                            target_ip.send(bytes(data,encoding='utf-8'))
                        else:
                            data_to_send = js.dumps({"status":"User not connected",'time_sent':str(datetime.now().strftime("%H:%m"))})
                            c.send(bytes(data_to_send,encoding='utf-8'))

            # if no data connection lost client connection closed close
            else:
                #displays disconnected client
                print("User '%s' disconnected at %s"%(username, datetime.now().strftime("%H:%m")))
                logging.debug("User '%s' disconnected at %s"%(username, datetime.now().strftime("%H:%m")))
                self.users.remove_by_name(username)
                c.close()
                break
    #server menu
    def menu(self):
        while True:
            print("\nCommands: \n1: List all clients\n0: Exit") 
            i = input()

            #Closes connections and exits server 
            if (i== "0"):
                data = {
                    'sender':"server",
                    'status':"shutting down"
                }
                #TODO Change this to get_all_conn
                users = self.users.get_all()

                for u in users:
                    target_ip = u[1]

                    #if target_ip not null senders name and message is sent to recipent
                    if(target_ip != None):
                        #create json object with username of sender and message so that the recpent knows who sent the message
                        print("Sending shutdown to %s"%(target_ip))
                        data = js.dumps(data)
                        target_ip.send(bytes(data,encoding='utf-8'))

                self.tcp_sock.close()
                print("Server closed") 
                logging.debug("Server stopped with command at %s"%(datetime.now().strftime("%H:%m")))
                logging.shutdown()
                sys.exit()

            #Lists all clients
            elif(i == "1"):
                no_of_users = self.users.get_no_of_users()
                print("No of users:"+str(no_of_users))
                #If there are currently clients connected, then prints name and connection
                if(no_of_users > 0):
                    info = self.users.get_all()
                    for i in info:
                        print("User: "+str(i[0]))
                        print("Conn: "+str(i[1]))
                else:
                    print("There are currently no clients connected")

            else:
                print("Please enter a valid command")

    #initializes server
    def run(self):

        #assigns server TCP ip, Port and receiving data buffer size
        tcp_ip = '127.0.0.1'
        tcp_port = 8080
        self.buf_size = 128
        
        #binds tcp socket and listens on it
        #if port in use, alt port num is used
        try :
            self.tcp_sock.bind((tcp_ip,tcp_port))
        except socket.error as e:
            logging.error("%s at %s"%(e,datetime.now().strftime("%H:%m")))
            if e.errno == errno.EADDRINUSE:
                logging.debug("Port %s in use, using alternative port"%(str(tcp_port)))
                print(("Port %s in use, using alternative port"%(str(tcp_port))))
                tcp_port = 10080
                self.tcp_sock.bind((tcp_ip,tcp_port))

        self.tcp_sock.listen(1)
        print('Server running')

        while True:
            #accepts incoming connect requests 
            c,a = self.tcp_sock.accept()

            #creates new client handler thread for each connected client
            handler_thread = threading.Thread(target=self.handler,args = (c,a))
            handler_thread.daemon =True
            handler_thread.start() 
            
        
server = Server()




