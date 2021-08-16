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

        self.username = input("enter username:   ")        
        self.tcp_port = 8080
        self.tcp_ip = '127.0.0.1'
        self.buff_size = 1024

        #if server port unavail try to connect to alternative port
        try:
            self.tcp_sock.connect((self.tcp_ip,self.tcp_port))
            self.send_user_data()
        except socket.error as error:
            print("using alt port")
            self.tcp_port = 10080
            self.tcp_sock.connect((self.tcp_ip,self.tcp_port))
            self.send_user_data()



        print("connected to server\n")


        #send key here
        #key = Key()
        #__pub_key = key.generate_private_key()
        #__priv_key = key.generate_private_key()
        #__p = key.get_P()

        #print(__pub_key)

        
        self.input_thread = threading.Thread(target=self.send_mesg)                        
        self.input_thread.daemon = True
        self.input_thread.start()

    #only run once!
    def send_user_data(self):
        data = self.username, self.tcp_ip
        self.tcp_sock.send(bytes(str(data),'utf-8'))
        pass

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


            
            if (str(self.mesg) == "exit"):
                self.tcp_sock.shutdown(1)
                self.tcp_sock.close()
                sys.exit(0)
                break

            self.tcp_sock.send(bytes(self.mesg,encoding='utf-8'))


           
if __name__ == "__main__":
    main()
