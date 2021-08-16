from socket import SocketKind

class User:
    __username: int
    __connection: SocketKind.SOCK_STREAM

    def __init__(self,username,conn):
        self.__username = username
        self.__connection = conn

    def get_username(self):
        return self.__username

    def get_connection(self):
        return self.__connection

    def set_connection(self, conn):
        self.__connection = conn

    