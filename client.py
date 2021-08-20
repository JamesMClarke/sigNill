from key import Key
import json as js
from datetime import datetime
import itertools, sys, socket, threading

#TODO if incoming message allow user to respond without having to declare who you want to send to -SC
#TODO add encrypt message
#TODO Store shared key after it has been generated maybe
#TODO Add load username, text colour from config json
#TODO Add choose text colour 

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



        if(self.load_user_config(config_file) and branch != "dev"):
            print(self.username)
        else:
            self.create_user()
            print(self.username)

        self.connect_to_server()
        self.menu()
       
    #sends username to server to be added to server users list
    def send_user_data(self):
         #Sends message to the server to say it has connected
        data = {
            'status':"connected",
            'sender':self.username
        }
        data = js.dumps(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))

    #handles data sent from the server
    def handler(self):

        #starts message input on seperate thread
        self.input_thread = threading.Thread(target=self.send_mesg)                        
        self.input_thread.daemon = True
        self.input_thread.start()

        self.handler_loop = True

        while self.handler_loop:    
            data = self.tcp_sock.recv(self.buff_size)
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
                    else:
                        print(data['status'])

                if not data:
                    print('Cannot connect to server')
                    break
            else:
                self.handler_loop = False
        
        self.menu()

    #sends message to server based on username of recipent who is set as target
    def send_mesg(self):
        target = input("Who do you want to message: " )
        
        self.mesg_loop = True
        while self.mesg_loop:
            mesg = input("type message:  ")
            #char limit on message
            #TODO Fix this, I think it can easily be tricked byt
            if(len(mesg)>50):
                print("There is a 50 character limit on messages")
                mesg = input("Type message:  ")
            
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
        print("commands:\n1: start chat\n2: edit username\n0: exit")
        cmd = input("enter command: ")
        if(cmd =="1"):
            try:
                self.connect_to_server()
            except OSError:
                pass
            self.handler()

        elif(cmd == "2"):
            #TODO Fully impellent changing username
            #If this is changed after the user has already connected to the server it will need to be changed there as well
            self.username = input("enter username:   ")
            pass
        elif(cmd =="0"):
            try:
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
        self.username = input("enter username:   ")
        if(len(self.username)>10):
            print("Username is limited to 10 characters")
            self.username = input("enter username:   ")
        #prevents blank username
        if(self.username ==""):
            self.create_user()

        self.username = self.sanitise_input(self.username)
        self.save_to_config(config_file)

     
    #loads user config infomation, if username not found in config returns null and runs create user
    def load_user_config(self,file):
        username_found = False
        try: 
            with open (file,"r") as read_file:
                data = js.load(read_file)
                print(data)
                if (data["configuration"][0]["username"]):
                    print('Welcome')
                    self.username = data ["configuration"][0]["username"]
                    username_found = True
                     
                elif ("username" not in data):
                    self.username = ""
                    print("No user found")

        except: 
            print("error in config")
        return username_found

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


    #sanitizes input strings
    def sanitise_input(self,input):
        #TODO Change sanitization to whitelist
        #array of characters to be removed from string
        s_list = ['?','.','!','/','#','$','%','<','>',':']
        translation = input.maketrans({i:"" for i in s_list})
        res_str = input.translate(translation)
        
        return res_str

            
           
if __name__ == "__main__":
    main()
