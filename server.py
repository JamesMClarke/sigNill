from datetime import datetime
import json as js
from keys import Keys
from key import Key
from os import error, mkdir
from users import Users
from tools import reg_input
import socket, errno,threading, sys, logging, bcrypt, os


reg_users_file = "data/reg_users.json"
branch = "dev"

#TODO Handle ConnectionResetError and remove from connected users
#TODO if client is registered send salt to client if not save client username and salt to reg_users
#Check that the logs folder exists and if it doesn't creates one
if(not os.path.isdir('logs')):
    os.mkdir('logs')
logging.basicConfig(filename="logs/"+str(datetime.now())+".log", level=logging.DEBUG)


class Server:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    users = Users()
    keys = Keys()

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
        while True:
            #loads data json object sent by client
            data = c.recv(self.buf_size)
            logging.debug("Server receive %s at %s"%(data, datetime.now().strftime("%H:%m")))
            if(data):
                print(data)
                data = js.loads(data)
  
                #direct messaging if keys target and message in data retrieves target ip by searching for username
                if ("target" in data):
                    target = str(data["target"])
                    #Server commands
                    if(target == "server"):
                        if('status' in data):
                            if(data['status'] == "connected"):
                                #TODO save username salt and password to server json file
                                #TODO add compare function for already existing user
                                #TODO Check if a user is already connected with that account name
                                username = data["sender"] 
                                salt =  data["data"]
                                print(salt)
                                self.check_user(username,salt,reg_users_file)                       
                                self.users.add_user(username, c)
                                print("User '%s' connected at %s"%(username, datetime.now().strftime("%H:%m")))
                                logging.debug("User '%s', '%s' , '%s' connected at %s"%(username,str(a[0]),str(a[1]), datetime.now().strftime("%H:%m")))

                        #If the data includes P and G then generate public key and send it back
                        elif('p' in data and 'g' in data):
                            p = int(data['p'])
                            g = int(data['g'])
                            key = Key(data['sender'], p, g)
                            self.keys.add_key(key)
                            #Generate and send public key
                            data = {
                                'target':data['sender'],
                                'time_sent':str(datetime.now().strftime("%H:%m")),
                                'sender':"server",
                                'key': key.generate_public_key().decode('utf-8')
                                }
                            data = js.dumps(data)
                            c.send(bytes(data,encoding='utf-8'))

                        #If the data includes their public key generate shaired key
                        elif('key' in data):
                            #Generate shaired key
                            key = self.keys.find_key_by_name(data['sender'])
                            if(not key.shared_set()):
                                key.generate_shared(data['key'])
                                print(key.get_shared())
                                
                        #If the message is encrypted
                        elif('nonce' in data):
                            if("message" in data):
                                self.forward(data['message'],data['nonce'],data['sender'])

            # if no data connection lost client connection closed close
            else:
                #displays disconnected client
                print("User '%s' disconnected at %s"%(username, datetime.now().strftime("%H:%m")))
                logging.debug("User '%s' disconnected at %s"%(username, datetime.now().strftime("%H:%m")))
                self.users.remove_by_name(username)
                c.close()
                break

    def kick(self, username):
        conn = self.users.find_conn_by_name(username)
        if(conn != None):
            #Sends data to tell users they have been kicked
            data = {
                'sender':"server",
                'status':"kicked"
            }
            data = js.dumps(data)
            conn.send(bytes(data,encoding='utf-8'))

            #Removes user from list of users
            self.users.remove_by_name(username)
            return True
        else:
            return False

    #server menu
    def menu(self):
        while True:
            print("\nCommands: \n1: List all clients\n2: Kick Client\n0: Exit") 
            i = reg_input("",int)

            #Closes connections and exits server 
            if (i== "0"):
                #This techincally doesn't currently need to be here
                #But I left it just incase we use it later
                data = {
                    'sender':"server",
                    'status':"shutting down"
                }
                conns = self.users.get_all_conn()

                for target_ip in conns:
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
            
            #Kick client
            elif(i == "2"):
                username = reg_input("Please enter the username of client you wish to kick:",str)
                if(self.kick(username)):
                    print("%s has been kicked"%(username))
                else:
                    print("%s is not currently connected"%(username))

            else:
                print("Please enter a valid command")


    #checks if user is in reg_user.json   
    def check_user(self,username,salt,file):
        try: 
            with open (file,"r") as read_file:
                data = js.load(read_file)
                data = data["registered_users"]
                #if data is empty add user
                if (len(data) == 0):
                    self.save_user_to_server_config(username,salt,reg_users_file)

                for i in data:
                    print(len(data))
                    if (username  != i["username"]):
                        #self.save_user_to_server_config(username,salt,reg_users_file)
                        print("user nto registered")

                    elif (username ==  i["username"]):
                        print("user already registered")                   
        
        except FileNotFoundError: 
            print("error no reg_user.json file found: "+str(FileNotFoundError))
        


    def save_user_to_server_config(self,__username,__salt,file):
        js_obj = {"username":str(__username),"salt":__salt }
        try:
            with open(file,"r+") as file:
                data = js.load(file)
                data['registered_users'].append(js_obj)
                file.seek(0)
                js.dump(data,file,indent=4)
                print("user saved to registered users")
        except FileNotFoundError:
            print("config not found")

   
    #initializes server
    def run(self):

        #assigns server TCP ip, Port and receiving data buffer size
        tcp_ip = '127.0.0.1'
        tcp_port = 8080
        self.buf_size = 2048
        
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
    
    def decrypt(self, message, sender, nonce):
        key = self.keys.find_key_by_name(sender)
        plaintext = key.decrypt(message, nonce)
        plaintext = plaintext.decode('utf-8')
        return plaintext

    #Encrypts and sends a message
    def encrypt_and_send_message(self, data, target):
        key = self.keys.find_key_by_name(target)
        if(key == None):
            return False
        print(data)
        ciphertext, nonce = key.encrypt(data)
        data = {
            'target':target,
            'message':ciphertext.decode('utf-8'),
            'nonce':nonce.decode('utf-8'),
            'time_sent':str(datetime.now().strftime("%H:%m")),
            'sender':"server"
            }
        data = js.dumps(data)
        conn = self.users.find_conn_by_name(target)
        conn.send(bytes(data,encoding='utf-8'))
        return True
    
    def encrypt_and_send_status(self, status, target):
        key = self.keys.find_key_by_name(target)
        if(key == None):
            return False
        ciphertext, nonce = key.encrypt(status)
        data = {
            'target':target,
            'status':ciphertext.decode('utf-8'),
            'nonce':nonce.decode('utf-8'),
            'time_sent':str(datetime.now().strftime("%H:%m")),
            'sender':"server"
            }
        data = js.dumps(data)
        conn = self.users.find_conn_by_name(target)
        conn.send(bytes(data,encoding='utf-8'))
        return True

    #Forwards on an encrypted message to the appropriate user
    def forward(self, message, nonce, sender):
        plaintext = self.decrypt(message, sender, nonce)
        data = js.loads(plaintext)
        target = data['target']
        print(target)
        data = js.dumps(data)
        if(target != "server"):
            #Checks user is still connected
            if(not self.encrypt_and_send_message(data,target)):
                #If they aren't then send a status message back
                status = "User "+target+" is not currently connected"
                self.encrypt_and_send_status(status, sender)



            
        
server = Server()




