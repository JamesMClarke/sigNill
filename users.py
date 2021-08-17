from array import array
from user import User

class Users:
    users : list

    def __init__(self):
        self.users = []

    def add_user(self, name, conn):
        self.users.append(User(name, conn))

    def find_conn_by_name(self,username_to_find):
        for u in self.users:
            if(username_to_find == u.get_username()):
                return u.get_connection()
                break
    
    def get_all_usernames(self):
        names = [0]
        for u in self.users:
            names.append(u.get_username())
        return names
    


