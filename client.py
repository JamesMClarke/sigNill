from re import I
from time import gmtime, sleep
from key import Key
import json as js
from datetime import datetime
from tools import reg_input
from keys import Keys
from key import Key
import itertools, sys, socket, threading, bcrypt, getpass

#TODO Store shared key after it has been generated maybe
#TODO Add text colour from config json
#TODO Add choose text colour 
#TODO Add password verification 
#TODO Add store freinds to config.json
#TODO if a username already exists do not create a new one
#TODO add create data folder and config.json file

config_file = 'data/config.json'
branch = "dev"
def main():
    
    client = Client()

class Client:
    
    #creates socket 
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    username = ""
    keys = Keys()
    server_key = Key('server')

    def __init__(self):
        #initializes connection variables
        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 1024
        
        self.load_user_config(config_file)

        self.connect_to_server()
        self.menu()
       
    #sends username to server to be added to server users list
    def send_user_data(self):
        #TODO add hashed password and salt to send 
        #Sends message to the server to say it has connected
        data = {
            'target':"server",
            'status':"connected",
            'sender':self.__username
            #'salt':str(self.salt)
        }
        data = js.dumps(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))

        #Send P and G
        #Generate and send public key
        #Wait for server to send public key back?


    #handles data sent from the server
    def handler(self):
        self.handler_loop = True
        
        while self.handler_loop:    
            data = self.tcp_sock.recv(self.buff_size)
            if(len(data) > 0):
                print(data)
                data = js.loads(data.decode('utf-8'))
                #If P and G are in the message
                if ('p' in data):
                    #Check if a user with that name is already in keys
                    if(self.keys.find_key_by_name(data['sender']) == None):
                        #If not create a new key
                        key = Key(data['sender'], int(data['p']), int(data['g']))
                        self.keys.add_key(key)
                        #Generate and send public key
                        data = {
                            'target':data['sender'],
                            'time_sent':str(datetime.now().strftime("%H:%m")),
<<<<<<< HEAD
                            'sender':self.username,
                            'key': key.generate_public_key().decode('utf-8')
=======
                            'sender':self.__username,
                            'key': key.generate_public_key()
>>>>>>> b2fe11cb67f2badb227019ddd78d2c0650216fad
                            }
                        print(data)
                        data = js.dumps(data)
                        self.tcp_sock.send(bytes(data,encoding='utf-8'))
                elif('key' in data):
                    #Generate shaired key
                    key = self.keys.find_key_by_name(data['sender'])
                    if(not key.shared_set()):
                        key.generate_shared(data['key'])
                        
                
                #If message sent from sender print
                if ('message' in data):
                    sender = data["sender"]
                    message = data['message']
                    #Nonce will only be in the data if it is encrypted
                    if('nonce' in data):
                        key = self.keys.find_key_by_name(sender)
                        message = key.decrypt(data['message'],data['nonce'])
                        message = message.decode('utf-8')

                    print(sender,": ",message)

                    #Sends received receipt
                    time_sent =datetime.now().strftime("%H:%m")
                    data = {
                        'target':sender,
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

                    #receives salt from server
                    if((data['sender'] == "server") and (data['data'])):
                        print("here is where the hwd comapre will run", data['sender'], data['data'])


                if not data:
                    print('Cannot connect to server')
                    break
            else:
                #TODO Make it handle this better than just closing the program
                print("Server has shutdown closing client")
                self.handler_loop = False
                self.tcp_sock.shutdown(0)
                self.tcp_sock.close()
                self.mesg_loop = False
                sys.exit("Client closing")
                quit()
        
        self.menu()

    #sends message to server based on username of recipient who is set as target
    def send_mesg(self):
        target = reg_input("Who do you want to message: ", str)
        #TODO Add encryption
        #Check if user is the one starting the conversation
        #TODO The client should probably check the user is a person on the server before key gen
        if(self.keys.find_key_by_name(target) == None):
            #If they are generate and send P and G to other user
            key = Key(target)
            self.keys.add_key(key)
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
            self.tcp_sock.send(bytes(data,encoding='utf-8'))
            #TODO Add check that they have received p and g
            #Generate public key and send public key
            data = {
                'target':target,
                'time_sent':str(datetime.now().strftime("%H:%m")),
<<<<<<< HEAD
                'sender':self.username,
                'key': key.generate_public_key().decode('utf-8')
=======
                'sender':self.__username,
                'key': key.generate_public_key()
>>>>>>> b2fe11cb67f2badb227019ddd78d2c0650216fad
                }
            print(data)
            data = js.dumps(data)
            self.tcp_sock.send(bytes(data,encoding='utf-8'))
            #Wait for shaired key to be generated
            while(not key.shared_set):
                sleep(1)
            #When you have received their shaired key generate shared key
            #Send encrypted message and nonce 
        self.mesg_loop = True
        while self.mesg_loop:
            mesg = reg_input("type message:  ", str)
            
                       
            if(mesg ==":q"):
                self.handler_loop = False
                self.mesg_loop = False
            else:   
                time_sent =datetime.now().strftime("%H:%m")
                key = self.keys.find_key_by_name(target)
                if(key != None):
                    message, nonce = key.encrypt(mesg)
                data = {
                    'target':target,
                    'message':message.decode('utf-8'),
                    'nonce':nonce.decode('utf-8'),
                    'time_sent':str(time_sent),
                    'sender':self.__username
                    }
                data = js.dumps(data)
                self.tcp_sock.send(bytes(data,encoding='utf-8'))
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

    #method to encrypt mesg
    def encrypt_mesg(self,mesg):
        encrypted = True
        spinner = itertools.cycle(['-','/','|','\\'])
        while encrypted == False:
            #shows loading spinner while message is being encrypted
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')

            #encrypt message here
            encrypted == True
        pass
    
    #user menu dislayed at start up
    def menu(self):
        self.handler_thread = threading.Thread(target = self.handler)
        self.handler_thread.daemon = True
        self.handler_thread.start()
        print("commands:\n1: start chat\n2: edit username\n0: exit")
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

        #lets user define their username
        self.__username = reg_input("enter username:   ", str)
        __password = getpass.getpass("enter password:   ")
        __password2 = getpass.getpass("renter password: ")

        #reruns create user if passwords do not match
        if(__password != __password2):
            print("passwords do not match")
            self.create_user()
        else:
            self.hash_pwd(__password)


        #TODO Fix this it can be easily tricked
        if(len(self.__username)>10):
            print("Username is limited to 10 characters")
            self.__username = reg_input("enter username:   ", str)
        

        #prevents blank username
        if(self.__username ==""):
            self.create_user()
        #passes password to be hashed
        self.hashed_password = (self.hash_pwd(__password))

        #dosent save to config if dev
        if(branch != "dev"):
            self.save_to_config(config_file)
        else:
            print("client in dev mode not saving client")

     
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
                    
               
        except : 
            print("error in config")

    # if no user in config saves username to config
    def save_to_config(self,file):
        js_obj ={"username":self.__username,"salt":str(self.salt,encoding='utf-8')}

        try:
            with open(file,"r+") as file:
                data = js.load(file)
                data['config'].append(js_obj)
                file.seek(0)
                js.dump(data,file,indent=4)
                print("user created\nWelcome: ",self.__username)
        except FileNotFoundError:
            print("config not found")

    
    #add loading indicator
    def hash_pwd(self,password):        
        password.encode("utf-8")
        self.salt = bcrypt.gensalt(rounds=16)
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"),bytes(self.salt))
        
        return hashed_pwd

    def compare_pwd(self,__salt,__hashed_pwd,__password):
            __allow_user_login = False
            __password = bcrypt.hashpw(__password.encode("utf-8"),bytes(__salt))
            
            if(__hashed_pwd == __hashed_pwd):
                print("password matches")
                __allow_user_login = True

            return __allow_user_login



           
if __name__ == "__main__":
    main()
