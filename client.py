from re import I
from time import gmtime, sleep,time
from key import Key
import json as js
from datetime import datetime
from tools import reg_input
from keys import Keys
from key import Key
from os.path import exists
import itertools, sys, socket, threading, bcrypt, getpass, os

#TODO Store shared key after it has been generated maybe
#TODO Add text colour from config json
#TODO Add choose text colour 
#TODO Add store freinds to config.json
#TODO if user already exists renter and hash pwd against stored hashed pwd, if 
# succesful connect to server send hashed pwd if match allow connect if not disconnects

#Add check that data/message has been received and if not resolve
#TODO PART 1: Add received messages to everything
#TODO PART 2: Check that they have been received
#TODO PART 3: If they haven't been received resolve

config_file = 'data/config.json'
branch = "dev"
def main():
    
    client = Client()

class Client:
    
    #creates socket 
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    __username = ""
    keys = Keys()
    server_key = Key('server')

    def __init__(self):


        
        #initializes connection variables
        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 2048
        #checks if data dir exists and created dir and config if not found
        if(not os.path.isdir('data')):
            self.create_config()

        
        self.load_user_config(config_file)

        self.connect_to_server()
        #self.encrypt_salt_pwd()
        self.menu()
       
    #sends username to server to be added to server users list
    def send_user_data(self):
        #TODO add hashed password and salt to send 
        #Sends message to the server to say it has connected
        data = {
            'target':"server",
            'status':"connected",
            #'data':str(self.__salt,encoding='utf-8'),
            #'data_2':str(self.hashed_password,encoding='utf-8'),
            'sender':self.__username
        }
        data = js.dumps(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))

        #Creates a key for the server
        self.create_key("server")
        #Wait for server to send public key back?


    #handles data sent from the server
    def handler(self):
        self.handler_loop = True
        
        while self.handler_loop:    
            data = self.tcp_sock.recv(self.buff_size)
            if(len(data) > 0):
                print(data)
                data = js.loads(data.decode('utf-8'))

                #If message sent from sender print
                if ('message' in data):
                    sender = data["sender"]
                    message = data['message']
                    #Nonce will only be in the data if it is encrypted
                    if('nonce' in data):
                        message = self.decrypt(message, sender, data['nonce'])
                        if(data['sender'] == "server"):
                            print(data)
                            data = js.loads(message)
                            sender = data['sender']

                            if("message" in data):
                                message = self.decrypt(data["message"], sender, data["nonce"])
                                print(sender,": ",message)

                            #If P and G are in the message
                            elif ('p' in data):
                                #Check if a user with that name is already in keys
                                if(self.keys.find_key_by_name(data['sender']) == None):
                                    #If not create a new key
                                    key = Key(data['sender'], int(data['p']), int(data['g']))
                                    self.keys.add_key(key)
                                    #Generate and send public key
                                    public_key = key.generate_public_key().decode('utf-8')
                                    self.send_public_key(public_key, data['sender'])

                            elif('key' in data):
                                if(data['sender'] == "server"):
                                    key = self.server_key
                                else:
                                    key = self.keys.find_key_by_name(data['sender'])
                                print(key)
                                print(data['sender'])
                                #Generate shaired key
                                if(not key.shared_set()):
                                    key.generate_shared(data['key'])
                                    print(key.get_shared())

                elif ('p' in data):
                        #Check if a user with that name is already in keys
                        if(self.keys.find_key_by_name(data['sender']) == None):
                            #If not create a new key
                            key = Key(data['sender'], int(data['p']), int(data['g']))
                            self.keys.add_key(key)
                            #Generate and send public key
                            public_key = key.generate_public_key().decode('utf-8')
                            self.send_public_key(public_key, data['sender'])

                elif('key' in data):
                    if(data['sender'] == "server"):
                        key = self.server_key
                    else:
                        key = self.keys.find_key_by_name(data['sender'])
                    print(key)
                    print(data['sender'])
                    #Generate shaired key
                    if(not key.shared_set()):
                        key.generate_shared(data['key'])
                        print(key.get_shared())

                    #Sends received receipt
                    time_sent =datetime.now().strftime("%H:%m")
                    data = {
                        'target':data['sender'],
                        'status':"Message received",
                        'time_sent':str(time_sent),
                        'sender': self.__username
                        }
                    data = js.dumps(data)
                    self.tcp_sock.send(bytes(data,encoding='utf-8'))
                    
                    
                elif ('status' in data):
                    if(data['status'] == "Message received"):
                        print(str(data['sender'])+" received your message")
                    if(data['sender'] == "server" and data['status'] == 'kicked'):
                        print("You have been kicked")
                        self.handler_loop = False
                        self.tcp_sock.shutdown(0)
                        self.tcp_sock.close()
                        self.mesg_loop = False
                        sys.exit("Client closing")
                        quit()
                    else:
                        print(data['status'])

                if not data:
                    print('Cannot connect to server')
                    break
            else:
                #When server stops, closes all loops and return to menu
                self.handler_loop = False
                self.mesg_loop = False


    #sends message to server based on username of recipient who is set as target
    def send_mesg(self):
        target = reg_input("Who do you want to message: ", str)
        #Check if user is the one starting the conversation
        #TODO The client needs to check if the user is online or on the server before continuing
        if(self.keys.find_key_by_name(target) == None):
            self.create_key(target)

        self.mesg_loop = True
        while self.mesg_loop:
            mesg = reg_input("type message:  ", str)
                       
            if(mesg ==":q"):
                self.handler_loop = False
                self.mesg_loop = False
            else:   
                time_sent =datetime.now().strftime("%H:%m")
                key = self.keys.find_key_by_name(target)
                try:
                    message, nonce = key.encrypt(mesg)
                    data = {
                        'target':target,
                        'message':message.decode('utf-8'),
                        'nonce':nonce.decode('utf-8'),
                        'time_sent':str(time_sent),
                        'sender':self.__username
                        }
                    data = js.dumps(data)
                    self.send_to_server(data)
                except:
                    print("Shared key has not been created yet")
                    print("Please try again a few seconds")
                    self.send_p_g(key, target)
                    #Gen public key
                    sleep(1)
                    #Send public key
                    self.send_public_key(key.get_public(),target)

        self.menu()

    #initializes connection to server 
    def connect_to_server(self):
        try:
            self.tcp_sock.connect((self.tcp_ip,self.tcp_port))
            self.send_user_data()
            print("connected to server")

        except socket.error as error:
            print("using alt port")
            self.tcp_port = 10080
            self.tcp_sock.connect((self.tcp_ip,self.tcp_port))
            self.send_user_data()
            print("connected to server")
    
    #user menu dislayed at start up
    def menu(self):
        while True:
            self.handler_thread = threading.Thread(target = self.handler)
            self.handler_thread.daemon = True
            self.handler_thread.start()
            print("Commands:\n1: start chat\n2: edit username\n0: exit")
            cmd = reg_input("enter command: ", int)
            if(cmd =="1"):
                #starts message input on seperate thread
                self.send_mesg()
            
            elif(cmd == "2"):
                #TODO Fully impellent changing username
                #If this is changed after the user has already connected to the server it will need to be changed there as well
                self.__username = reg_input("enter username:   ", str)
                pass
            elif(cmd =="0"):
                try:
                    time_sent =datetime.now().strftime("%H:%m")

                    data = {
                        'target':"server",
                        'status':'disconnecting',
                        'time_sent':str(time_sent),
                        'sender':self.__username
                        }

                    data = js.dumps(data)
                    self.tcp_sock.send(bytes(data,encoding='utf-8'))

                    self.tcp_sock.shutdown(0)
                    self.tcp_sock.close()
                except OSError:
                    pass
                sys.exit("Client closing")
                quit()
            else:
                print("Invalid command")

    #if users is not found in config.json, creates username
    def create_user(self):
        password_match = False
        self.__username = reg_input("enter username:   ", str)
        if (self.__username ==""):
                self.__username = reg_input("enter username:   ", str)

        valid = False
        while not valid:
            if(len(self.__username)>10):
                print("Username is limited to 10 characters")
                self.__username = reg_input("enter username:   ", str)
            else:
                valid = True

        while password_match == False:
            __password = getpass.getpass("enter password:   ")
            __password2 = getpass.getpass("renter password: ")

            #reruns create user if passwords do not match
            if(__password != __password2):
                print("passwords do not match")
            else:
                password_match = True
         
        self.hash_pwd(__password)
        
        
       
        #passes password to be hashed
        self.hashed_password = (self.hash_pwd(__password))

        #dosent save to config if dev
        if(branch == "dev"):
            self.save_to_config(config_file)
        else:
            
            print("client in dev mode not saving client\nUser:",self.__username)

     
    #loads user config infomation, if username not found in config returns null and runs create user
    def load_user_config(self,file):
        try: 
            with open (file,"r") as read_file:
                data = js.load(read_file)
                data = data['config']
                if (len(data)==0):                                          
                    print("No user found: Creating User")
                    self.create_user()
                
                elif("username"  in data[0]):
                    self.__username = data[0]['username'] 
                    self.__salt = data[0]['salt']
                    print("Welcome: ",self.__username) 
                    
               
        except FileNotFoundError: 
            print("error in config")

    # if no user in config saves username to config
    def save_to_config(self,file):
        js_obj ={"username":self.__username,"salt":str(self.__salt,encoding='utf-8'),"hashpwd":str(self.hashed_password,encoding='utf-8')}

        try:
            with open(file,"r+") as file:
                data = js.load(file)
                data['config'].append(js_obj)
                file.seek(0)
                js.dump(data,file,indent=4)
                print("user created\nWelcome: ",self.__username)
        except FileNotFoundError:
            print("config not found")

    def create_config(self):
        os.mkdir('data')
        file_name ="data/config.json"
        file_exists = exists(file_name)
        if(file_exists is None):
            config = {
                "config": [

                    ]
                }   
            with open(file_name,"rw") as file:
                json_obj = js.dumps(config)
                file.write(json_obj)
        
    def encrypt_salt_pwd(self):
        e_pwd,e_salt = self.server_key.encrypt(self.hashed_password,self.__salt)
        print(e_pwd,e_salt)
        pass
    
    def loading(self,loading_str):
        chars = "/-\|"
        while self.complete == False:
            for char in chars:
                sys.stdout.write('\r'+loading_str+str(char))
                sleep(0.15)
                sys.stdout.flush()

            if self.complete == True:
                    sys.stdout.write("\rdone")
                    break



    #add loading indicator
    def hash_pwd(self,password):
        self.complete = False
        self.loading_str = "hashing password: "        
        password.encode("utf-8")
        self.__salt = bcrypt.gensalt(rounds=16)
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"),bytes(self.__salt))
        self.complete = True

        
        return hashed_pwd

    def compare_pwd(self,__salt,__hashed_pwd,__password):
            __allow_user_login = False
            __password = bcrypt.hashpw(__password.encode("utf-8"),bytes(__salt))
            
            if(__hashed_pwd == __hashed_pwd):
                print("password matches")
                __allow_user_login = True

            return __allow_user_login

    def create_key(self, target):
            #Generate and send P and G to other user
            if(target != "server"):
                key = Key(target)
                self.keys.add_key(key)
            else:
                key = self.server_key

            sleep(1)
            #Send p and g
            self.send_p_g(key, target)
            #Gen public key
            sleep(1)
            public_key = key.generate_public_key().decode('utf-8')
            print(public_key)
            #Send public key
            self.send_public_key(public_key,target)
            

    def send_p_g(self, key, target):
        P, G = key.get_P_G()
        #Send P and G
        data = {
                'target':target,
                'time_sent':str(datetime.now().strftime("%H:%m")),
                'sender':self.__username,
                'p': str(P),
                'g': str(G)
                }
        data = js.dumps(data)
        if(target == "server"):
            self.tcp_sock.send(bytes(data,encoding='utf-8'))
        else:
            self.send_to_server(data)

    def send_public_key(self, public_key, target):
        data = {
                'target':target,
                'time_sent':str(datetime.now().strftime("%H:%m")),
                'sender':self.__username,
                'key': public_key
                }
        data = js.dumps(data)
        if(target == "server"):
            self.tcp_sock.send(bytes(data,encoding='utf-8'))
        else:
            self.send_to_server(data)


    #Encrypts the whole message and sends it to sever within it's own message
    def send_to_server(self, data):
        print(data)
        ciphertext, nonce = self.server_key.encrypt(data)
        data = {
            'target':'server',
            'message':ciphertext.decode('utf-8'),
            'nonce':nonce.decode('utf-8'),
            'time_sent':str(datetime.now().strftime("%H:%m")),
            'sender':self.__username
            }
        data = js.dumps(data)
        try:
            self.tcp_sock.send(bytes(data,encoding='utf-8'))
        except:
            print("Server is currently closed")
            self.handler_loop = False
            self.mesg_loop = False

    def decrypt(self, message, sender, nonce):
        if(sender != "server"):
            key = self.keys.find_key_by_name(sender)
        else:
            key = self.server_key
        plaintext = key.decrypt(message, nonce)
        plaintext = plaintext.decode('utf-8')
        return plaintext



           
if __name__ == "__main__":
    main()
