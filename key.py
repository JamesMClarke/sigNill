import os
from Crypto.Util import number

class key:
<<<<<<< HEAD
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
=======
    _key_bits = 4096
    _P: int
    _G: int
    _private: int
    _public: int
    _shared: int

    def __init__(self, *args):
        #If P and G are already set, then set them
        if len(args) != 0:
            self._P = args[0]
            self._G = args[1]
            self.generate_private_key()
        #Else create them
        else:
            self._P = number.getPrime(self._key_bits)
            self._G = number.getPrime(self._key_bits)
            self.generate_private_key()
        
    #Generates a random private key
    def generate_private_key(self) -> bytes:
        self._private = int.from_bytes(os.urandom(self._key_bits//8), "big")

    #Generates the public key to be shared
    def generate_public_key(self):
        self._public = pow(self._G, self._private, self._P)
        return self._public

    #Generates the shared private key
    def generate_shared(self, public2):
        #self.shared = (public2**self.private)%self.P
        self._shared = pow(public2, self._private, self._P)

    def get_P(self):
        return self._P
    
    def get_G(self):
        return self._G

    def get_shared(self):
        return self._shared
>>>>>>> d04d1611c4546f2435adfc557c7c50a7ccaaf761

Alice = key()
P = Alice.get_P()
G = Alice.get_G()
Bob = key(P,G)
<<<<<<< HEAD
=======
print(Bob.get_P(), Bob.get_G())
>>>>>>> d04d1611c4546f2435adfc557c7c50a7ccaaf761
print("Gen public")
Alice_Public = Alice.generate_public_key()
Bob_public = Bob.generate_public_key()
print("Gen shared")
Alice.generate_shared(Bob_public)
Bob.generate_shared(Alice_Public)
<<<<<<< HEAD
print(Alice.shared)
print(Bob.public)
=======
print(Alice.get_shared())
print(Bob.get_shared())
>>>>>>> d04d1611c4546f2435adfc557c7c50a7ccaaf761

