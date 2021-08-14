import socket
import threading
import sys

class Client:
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def __init__(self):
        tcp_port = 8080
        tcp_ip = '127.0.0.1'
        buff_size = 1024


        self.tcp_sock.connect((tcp_ip,tcp_port))
        

        input_thread = threading.Thread(target=self.send_mesg)
        input_thread.daemon = True
        input_thread.start()

        while True:
            data = self.tcp_sock.recv(buff_size)
            print(data)
            if not data:
                print('cannot connect to server')
                break
            print(str(data,'utf-8'))


        


    def send_mesg(self):
      
        while True:
            
            mesg = input()
            self.tcp_sock.send(bytes(mesg,'utf-8'))
            if( mesg =='exit'):
                self.tcp_sock.close()
                exit()
client = Client()