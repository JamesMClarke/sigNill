import os
from Crypto.Util import number

class key:
    key_bits = 32
    P: int
    G: int
    private: int
    public: int
    shared: int

    def __init__(self, *args):
        if len(args) != 0:
            self.P = args[0]
            self.G = args[1]
            self.generate_private_key()
        else:
            self.P = number.getPrime(self.key_bits//2)
            self.G = number.getPrime(self.key_bits//2)
            print(self.P,self.G)
            self.generate_private_key()
        

    def generate_private_key(self) -> bytes:
        self.private = int.from_bytes(os.urandom(self.key_bits // 8 + 8), byteorder="big")
        print(self.private)

    def generate_public_key(self):
        self.public = (self.G**self.private)%self.P
        return self.public

    def generate_shared(self, public2):
        self.shared = (public2**self.private)%self.P

    def get_P(self):
        return self.P
    
    def get_G(self):
        return self.G

Alice = key()
P = Alice.get_P()
G = Alice.get_G()
Bob = key(P,G)
print("Gen public")
Alice_Public = Alice.generate_public_key()
Bob_public = Bob.generate_public_key()
print("Gen shared")
Alice.generate_shared(Bob_public)
Bob.generate_shared(Alice_Public)
print(Alice.shared)
print(Bob.public)

