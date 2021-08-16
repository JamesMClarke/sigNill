class User:

    def __init__(self,username,addr):
        self.__username = username
        self.__addr = addr

    def get_username(self):
        return self.__username

    def get_addr(self):
        return self.__addr

    