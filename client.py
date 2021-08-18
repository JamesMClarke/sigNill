import socket
import threading
import sys
from key import Key
import json as js

#TODO sanitize input
#TODO if incoming message allow response without having to declare who you want to send to
#TODO add menu
def main():
    
    client = Client()
    client.handler()



class Client:

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    username = ""

    def __init__(self):

        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 1024

        self.username = input("enter username:   ")
        #print("Avaiblable commands\n0: exit\n1: start a chat")
        #command = input("Input Command")
        self.connect_to_server()
        
        self.input_thread = threading.Thread(target=self.send_mesg)                        
        self.input_thread.daemon = True
        self.input_thread.start()

       
    #only run once!
    def send_user_data(self):
        
        data = js.dumps({'username':self.username})
        print(data)
        self.tcp_sock.send(bytes(data,encoding='utf-8'))

    def handler(self):
   
        while True:    
            data = self.tcp_sock.recv(self.buff_size)
            print(data)

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
            data = {
                'target':target,
                'message':mesg
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

    
           
if __name__ == "__main__":
    main()
