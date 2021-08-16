import socket
import threading
import sys
from key import Key

#TODO redo threading and application func flow
#TODO fix UI bug
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
        
        self.tcp_sock.connect((self.tcp_ip,self.tcp_port))
        print("connected to server\n")
        #self.username = input("enter username:   ")
        #data = self.username,"|",self.tcp_ip

        #self.tcp_sock.send(bytes(str(data),encoding='utf-8'))

        #send key here
        #key = Key()
        #__pub_key = key.generate_private_key()
        #__priv_key = key.generate_private_key()
        #__p = key.get_P()

        #print(__pub_key)

        
        self.input_thread = threading.Thread(target=self.send_mesg)                        
        self.input_thread.daemon = True
        self.input_thread.start()


    def handler(self):

       

            
        while True:    
            data = self.tcp_sock.recv(self.buff_size)
            data = str(data,'utf-8')
            print(data)

            #if(data =="client connected"):
             #   test_data = "test"
              #  self.tcp_sock.send(bytes(test_data,encoding='utf-8'))




            
            

           



                
            if not data:
                print('cannot connect to server')
                print(str(data,'utf-8'))
                break


    def send_mesg(self):

      
        while True:
            self.mesg = input("type message:  ")


            
            #if (str(mesg) == "exit"):
             #   self.tcp_sock.close()
#                sys.exit(0)

            self.tcp_sock.send(bytes(self.mesg,encoding='utf-8'))


           
if __name__ == "__main__":
    main()
