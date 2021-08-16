from json import decoder
import socket
import threading
import sys
import json as js

#TODO redo threading and application func flow
def main():
    
    client = Client()
    client.connect_to_server()


class Client:

    def __init__(self):

        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 1024
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect_to_server(self):

        self.tcp_sock.connect((self.tcp_ip,self.tcp_port))
        print("connected to server")

            
        while True:    
            data = self.tcp_sock.recv(self.buff_size)
            data = str(data,'utf-8')
            print(data)

            
            self.input_thread = threading.Thread(target=self.send_mesg)                        
            self.input_thread.daemon = True
            self.input_thread.start()



                
            if not data:
                print('cannot connect to server')
                print(str(data,'utf-8'))
                break


    def send_mesg(self):
      
        while True:
            #mesg =""
            mesg = input("type message:  ")
            
            #if (str(mesg) == "exit"):
             #   self.tcp_sock.close()
#                sys.exit(0)

            self.tcp_sock.send(bytes(mesg,encoding='utf-8'))


           
if __name__ == "__main__":
    main()
