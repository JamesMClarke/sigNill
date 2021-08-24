from key import Key
import json as js
from datetime import datetime
from tools import reg_input
import itertools, sys, socket, threading, bcrypt, getpass

#TODO add encrypt message
#TODO Store shared key after it has been generated maybe
#TODO Add text colour from config json
#TODO Add choose text colour 
#TODO Add password verification 
#TODO Add store freinds to config.json
#TODO  if a username already exists do not create a new one
#TODO add create data folder and config.json file

config_file = 'data/config.json'
branch = "dev"
def main():
    
    client = Client()

class Client:
    
    #creates socket 
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    username = ""

    def __init__(self):
        #initializes connection variables
        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 1024

        self.load_user_config(config_file)
        if((self.username == "") and(branch !="dev")):
            self.create_user()
            print(self.username)
        else:
            print(self.username)

        self.connect_to_server()
        self.menu()
       
    #sends username to server to be added to server users list
    def send_user_data(self):
        #TODO add hashed password and salt to send 
        #Sends message to the server to say it has connected
        data = {
            'target':"server",
            'status':"connected",
            'sender':self.username,
            'password':str(self.hashed_password),
            'salt':str(self.salt)
        }
        data = js.dumps(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))

    #handles data sent from the server
    def handler(self):
        self.handler_loop = True

        while self.handler_loop:    
            data = self.tcp_sock.recv(self.buff_size)
            print(data)
            print(len(data))
            if(len(data) > 0):
                data = js.loads(data.decode('utf-8'))
                #If message sent from sender print
                if ('message' in data):
                    sender = data["sender"]
                    print(sender,": ",data['message'])

                    #Sends received receipt
                    time_sent =datetime.now().strftime("%H:%m")
                    data = {
                        'target':sender,
                        'status':"Message received",
                        'time_sent':str(time_sent),
                        'sender': self.username
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
                #TODO Make it handle this better than just closing the program
                print("Server has shutdown closing client")
                self.handler_loop = False
                self.tcp_sock.shutdown(0)
                self.tcp_sock.close()
                self.mesg_loop = False
                sys.exit("Client closing")
                quit()
        
        self.menu()

    #sends message to server based on username of recipent who is set as target
    def send_mesg(self):
        target = reg_input("Who do you want to message: ", str)
        
        self.mesg_loop = True
        while self.mesg_loop:
            mesg = reg_input("type message:  ", str)
            #char limit on message
            valid = False
            while not valid:
                if(len(mesg)<50):
                    valid = True
                else:
                    print("There is a 50 character limit on messages")
                    mesg = reg_input("Type message:  ", str)
            
            if(mesg ==":q"):
                self.handler_loop = False
                self.mesg_loop = False
            else:
                mesg = self.sanitise_input(mesg)        
                time_sent =datetime.now().strftime("%H:%m")

                data = {
                    'target':target,
                    'message':mesg,
                    'time_sent':str(time_sent),
                    'sender':self.username
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
    
    #method to send pulbic key
    def send_pub_key(self):
     
        pass

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
            self.username = reg_input("enter username:   ", str)
            pass
        elif(cmd =="0"):
            try:
                time_sent =datetime.now().strftime("%H:%m")

                data = {
                    'target':"server",
                    'status':'disconnecting',
                    'time_sent':str(time_sent),
                    'sender':self.username
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
        self.username = reg_input("enter username:   ", str)
        __password = getpass.getpass("enter password:   ")

        #TODO Fix this it can be easily tricked
        if(len(self.username)>10):
            print("Username is limited to 10 characters")
            self.username = reg_input("enter username:   ", str)
        #prevents blank username
        if(self.username ==""):
            self.create_user()
        
        self.hashed_password = (self.hash_pwd(__password))
        print(self.hashed_password)
        self.save_to_config(config_file)

     
    #loads user config infomation, if username not found in config returns null and runs create user
   def load_user_config(self,file):
        try: 
            with open (file,"r") as read_file:
                data = js.load(read_file)
                data = data['configuration']
                for i in data:
                    if (i["username"]):
                        self.username = i["username"]               
                    elif (i["username"] not in data):
                        self.username = ""
                        print("No user found")

                return self.username
        except: 
            print("error in config")

    # if no user in config saves username to config
    def save_to_config(self,file):
        js_obj ={"username":self.username}

        try:
            with open(file,"r+") as file:
                data = js.load(file)
                data['configuration'].append(js_obj)
                file.seek(0)
                js.dump(data,file,indent=4)
        except FileNotFoundError:
            print("config not found")

    
    #add loading indicator
    def hash_pwd(self,password):        
        password.encode("utf-8")
        self.salt = bcrypt.gensalt(rounds=16)
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"),bytes(self.salt))
        
        return hashed_pwd
  
           
if __name__ == "__main__":
    main()
