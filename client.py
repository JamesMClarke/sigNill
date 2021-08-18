import socket
import threading
from key import Key
import json as js
from datetime import datetime

#TODO if incoming message allow reponse response without having to declare who you want to send to -SC
#TODO make username only have to be set once and then save to a config file as xml or json confer with -JC
#TODO add encrypt message
#TODO add menu

def main():
    
    client = Client()
    #client.handler()



class Client:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    username = ""

    def __init__(self):

        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 1024


        self.username = input("enter username:   ")

        self.connect_to_server()
        self.handler()
       
    #only run once!
    def send_user_data(self):
        
        data = js.dumps({'username':self.username})
        print(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))

    def handler(self):
   
        self.input_thread = threading.Thread(target=self.send_mesg)                        
        self.input_thread.daemon = True
        self.input_thread.start()

        while True:    
            data = self.tcp_sock.recv(self.buff_size)
            data = js.loads(data.decode('utf-8'))

            # gets target might remove
            if("target" in data):
                sender = data["target"]
                recv_message = data["message"]
                print(sender,": ",recv_message)

            #if message sent from sender print
            if all(key in data for key in ("username","message")):
                print(data["username"],": ",data['message'])

            if not data:
                print('cannot connect to server')
                break

    def send_mesg(self):

        target = input("Who do you want to message: " )
        while True:
            mesg = input("type message:  ")
            time_sent = "  time sent:"+datetime.now().strftime("%H:%m")
            data = {
                'target':target,
                'message':mesg+str(time_sent)
                }

            data = js.dumps(data)
            self.tcp_sock.send(bytes(data,encoding='utf-8'))

        
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
    
    def send_pub_key(self):
        pass
    
    def encrypt_mesg(self,mesg):
        pass
    
           
if __name__ == "__main__":
    main()
