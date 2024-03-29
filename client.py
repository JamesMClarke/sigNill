from re import I
from time import gmtime, sleep,time
from key import Key
import json as js
from datetime import datetime
from tools import reg_input
from keys import Keys
from key import Key
from os.path import exists
import sys, socket, threading, bcrypt, os

#TODO Store shared key after it has been generated maybe
#TODO Add text colour from config json
#TODO Add choose text colour 
#TODO Add store friends to config.json

#TODOAdd received messages to everything
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
    __salt = ""
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
        self.handler_thread = threading.Thread(target = self.handler)
        self.handler_thread.daemon = True
        self.handler_thread.start()
        #TODO Check if user is already on the server, if not get them to create a password
        #TODO If user is on server get salt, hash password+salt, and send this back
        #TODO Once a user logs in store a token rather than their hashed password
        sleep(1)
        #Sends hashed user password and salt to the server
        #TODO Only send this when creating a user
        self.send("server", "r_pwd",self.hashed_password, True, "r_salt",self.__salt)
        self.menu()

    #handles data sent from the server
    def handler(self):
        self.handler_loop = True
        
        while self.handler_loop:    
            data = self.tcp_sock.recv(self.buff_size)
            if(len(data) > 0):
                print(data)
                data = js.loads(data.decode('utf-8'))
                sender = data["sender"]
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
                                self.received_receipt(sender,"message")

                            #If P and G are in the message
                            elif ('p' in data):
                                self.gen_public_from_p_g(data)
                                self.received_receipt(sender,"pandg")

                            #If the keys in the message
                            elif('key' in data):
                                self.gen_shared(data)
                                self.received_receipt(sender,"key")
                            
                            #Handels received receipts
                            elif('received' in data):
                                print("The %s was received"%(data['received']))

                #Handels gening public for server
                elif ('p' in data):
                    self.gen_public_from_p_g(data)
                    self.received_receipt(sender,"pandg")
                
                #Handles gening shared key for the server
                elif('key' in data):
                    self.gen_shared(data)
                    self.received_receipt(sender,"key")
                    
                elif ('status' in data):
                    if(data['status'] == "Message received"):
                        print(str(data['sender'])+" received your message")
                    if(data['sender'] == "server" and data['status'] == 'kicked'):
                        print("You have been kicked")
                        self.shutdown_client()

                    if(data['sender']=="server" and data['status']=="User bob already connected"):
                        print ('user already connected shutting down')
                        self.shutdown_client()

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
                    #Sends encrypted message
                    self.send(target, "message", mesg, True)
                except:
                    print("Shared key has not been created yet")
                    print("Please try again a few seconds")
                    #Sends p and g
                    self.send(target,"p",key.get_P(),False,"g",key.get_G())
                    sleep(1)
                    #Send public key
                    self.send(target, 'key', key.get_public())

        self.menu()

    #initializes connection to server 
    def connect_to_server(self):
        try:
            self.tcp_sock.connect((self.tcp_ip,self.tcp_port))

        except socket.error as error:
            print("Using alt port")
            self.tcp_port = 10080
            self.tcp_sock.connect((self.tcp_ip,self.tcp_port))

        self.send("server","status","connected")
        print("Connected to server")
        #Creates a key for the server
        self.create_key("server")
    
    #user menu dislayed at start up
    def menu(self):
        while True:
            print("Commands:\n1: start chat\n2: edit username\n0: exit")
            cmd = reg_input("enter command: ", int)
            if(cmd =="1"):
                #Starts messaging input on main thread
                self.send_mesg()
            
            elif(cmd == "2"):
                #TODO Fully impellent changing username
                #If this is changed after the user has already connected to the server it will need to be changed there as well
                self.__username = reg_input("enter username:   ", str)
                pass
            elif(cmd =="0"):
                try:
                    #Sends disconnecting message to the server
                    self.send("server","status","disconnecting")
                    self.shutdown_client()

                except OSError:
                    pass
                sys.exit("Client closing")
                quit()
            else:
                print("Invalid command")

    
    #if users is not found in config.json, creates username
    def create_user(self):
        #on create_user, encrypt salt and hashed password and send to server
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
                self.create_password()

    def create_password(self):
        password_match = False
        while password_match == False:
            password = reg_input("Enter password:   ", "pwd")
            password1 = reg_input("Renter password:   ", "pwd")

            #reruns create user if passwords do not match
            if(password != password1):
                print("passwords do not match")
            else:
                password_match = True
         
        #passes password to be hashed       
        loading = threading.Thread(target=self.loading_animation)
        self.loading_str = "hashing password: "
        self.complete = False
        loading.start()
        self.hashed_password = (str(self.hash_password_func(password),encoding='utf-8'))
        self.complete = True
        loading.join()


        #Doesn't save to config if dev
        if(branch != "dev"):
            self.save_to_config(config_file)
        else:
            
            print("client in dev mode not saving client\nUser:",self.__username)

     
    #loads config into memory
    def load_user_config(self,file):
        try: 
            with open (file,"r") as read_file:
                data = js.load(read_file)
                data = data['config']
                self.load_username(data)

        except FileNotFoundError: 
            print("config.json not found")

    #loads username from config if username None creates user
    def load_username(self,data):
        if (len(data)==0 or branch=="dev"):    
                print("No user found: Creating User")
                self.create_user()

        #if username in config.json self.username value is set to that
        for i in data:
            if(i['username']):
                self.__username = i['username'] 
                print("Welcome: ",self.__username) 
                self.__salt = i['salt']
                self.__password = reg_input("Enter password:    ","pwd")
   
    # if no user in config saves username to config
    def save_to_config(self,file):
        js_obj ={"username":self.__username,"salt":str(self.__salt,encoding='utf-8')}

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
        
  
    def loading_animation(self):
        chars = "/-\|"
        while self.complete == False:
            for char in chars:
                sys.stdout.write('\r'+self.loading_str+str(char))
                sleep(0.12)
                sys.stdout.flush()

            if self.complete == True:
                    sys.stdout.flush()
                    sys.stdout.write("\rdone")
                    break

    #user client login send encrypted non hashed_pwd
    def user_login(self):
        password_to_send = bcrypt.hashpw(self.__password,self.__salt)
        ciphertext,nonce = self.server_key.encrypt(password_to_send)

        data = {
            'target':'server',
            'l_pwd':ciphertext.decode('utf-8'),
            'nonce':nonce.decode('utf-8'),
            'time_sent':str(datetime.now().strftime("%H:%m")),
            'sender':self.__username
            }

        data = js.dumps(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))    


    #add loading indicator
    def hash_password_func(self,password):
        password.encode("utf-8")
        self.__salt = bcrypt.gensalt(rounds=16)
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"),bytes(self.__salt))
        self.__salt = str(self.__salt,encoding='utf-8')

        return hashed_pwd

    def create_key(self, target):
            #Generate and send P and G to other user
            if(target != "server"):
                key = Key(target)
                self.keys.add_key(key)
            else:
                key = self.server_key

            sleep(1)
            #Sends p and g
            self.send(target,"p",key.get_P(),False,"g",key.get_G())
            #Gen public key
            #Gen public key
            pub = key.generate_public_key()
            sleep(1)
            #Send public key
            self.send(target, 'key', pub)

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
    
    def gen_shared(self, data):
        if(data['sender'] == "server"):
            key = self.server_key
        else:
            key = self.keys.find_key_by_name(data['sender'])
        #Generate shaired key
        if(not key.shared_set()):
            key.generate_shared(data['key'])
            print("shared key",key.get_shared())
            print(key)
    
    def gen_public_from_p_g(self, data):
        #Check if a user with that name is already in keys
        if(self.keys.find_key_by_name(data['sender']) == None):
            #If not create a new key
            key = Key(data['sender'], int(data['p']), int(data['g']))
            self.keys.add_key(key)
            #Generate and send public key
            public_key = key.generate_public_key()
            self.send(data['sender'], 'key', public_key)

    #Creates and sends a received receipt back to the sender
    def received_receipt(self, sender, type):
        self.send(sender,"received", type)

    def send(self, target, type, data, encrypted = False, type2 = False, data2= False):
        if(encrypted):
            if(target != "server"):
                key = self.keys.find_key_by_name(target)
            else:
                key = self.server_key
            data, nonce = key.encrypt(data)
            data = data.decode('utf-8')
            nonce = nonce.decode('utf-8')
            if(data2 != False):
                #Encrypt data and data2
                data2, nonce2 = key.encrypt(data2)
                data2 = data2.decode('utf-8')
                nonce2 = nonce2.decode('utf-8')
        d = {
            'target':target,
            type : data,
            'time_sent':str(datetime.now().strftime("%H:%m")),
            'sender':self.__username
        }
        if(encrypted):
            n = {'nonce':nonce}
            d.update(n)
        if(data2 != False):
            two = {'type2': data2}
            if(encrypted):
                two = {type2: data2, 'nonce2':nonce2}
            else:
                two = {type2: data2}
            d.update(two)
        print(d)
        d = js.dumps(d)
        print("Send test")
        print(d)
        if(target == "server"):
            self.tcp_sock.send(bytes(d,encoding='utf-8'))
        else:
            self.send_to_server(d)

    def shutdown_client(self):
            self.handler_loop = False
            self.tcp_sock.shutdown(0)
            self.tcp_sock.close()
            self.mesg_loop = False
            self.handler_thread.join()
            sys.exit("Client closing")
            

           
if __name__ == "__main__":
    main()
