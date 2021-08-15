from json import decoder
import socket
import threading
import sys
import json as js


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
        

        while True:
            
            data = self.tcp_sock.recv(self.buff_size)
            data = str(data,'utf-8')
            print(data)
            data = js.loads(data)

            if ("status" in data):
                if (data['status'] == 'ok'):
                    print("connected to server")
                    input_thread = threading.Thread(target=self.send_mesg)
                    input_thread.daemon = True
                    input_thread.start()

                elif(data["status"] =='fail'):
                    print("cannot connect to server")
                    
                    #sys.exit()

            if("msg" in data):
                print("message",data['msg'])

        
            
            
            if not data:
                print('cannot connect to server')
                break
            #print(str(data,'utf-8'))

    def send_mesg(self):
      
        while True:
            
            mesg = input()
            json_mesg = {"mesg":mesg}
            #converts to json
            json_mesg = js.dumps(json_mesg)
            self.tcp_sock.send(bytes(json_mesg,encoding='utf-8'))


            if( mesg =='exit'):
                self.tcp_sock.close()
                exit()

if __name__ == "__main__":
    main()
