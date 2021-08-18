from array import array
from user import User

class Users:
    users : list

    def __init__(self):
        #Initialise the list
        self.users = []

    def add_user(self, name, conn):
        #Adds a users name and connection info to the list
        self.users.append(User(name, conn))

    #Searches the list to find a user via their name
    def find_conn_by_name(self,username_to_find):
        for u in self.users:
            if(username_to_find == u.get_username()):
                return u.get_connection()
            else:
                print("no user")
            
    #Returns a list of usernames
    def get_all_usernames(self):
        names = []
        for u in self.users:
            names.append(u.get_username())
        return names
    
    #Returns all info about a user
    def get_all(self):
        info = []
        for u in self.users:
            info.append([u.get_username(), u.get_connection()])
        return info

    #Returns the number of uses
    def get_no_of_users(self):
        return len(self.users)
    


