from key import Key

class Keys:
    keys : list

    def __init__(self):
        self.keys = []
    
    def add_key(self, key):
        self.keys.append(key)
    
    def get_key_in_pos(self, pos):
        return self.keys[pos]
    
    def find_key_by_name(self, name):
        for k in self.keys:
            if(k.get_user() == name):
                return k
        return None