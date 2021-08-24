import base64
import os, codecs, math
from Crypto.Cipher import AES
from Crypto.Util import number
from time import time


class Key:
    _key_bits = 256
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

    #Encrypts the messages using AES and returns it in base 64
    def encrypt(self, plaintext):
        cipher = AES.new(self._shared.to_bytes(32,'big'), AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        message = base64.b64encode(ciphertext)
        return message, nonce
    
    #Takes the encrypted message in base 64 and decrypts it
    def decrypt(self, message, nonce):
        ciphertext = base64.b64decode(message)
        cipher = AES.new(self._shared.to_bytes(32,'big'), AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext

"""
#Example set-up
start = time()
Alice = Key()
P = Alice.get_P()
G = Alice.get_G()
Bob = Key(P,G)
print(Bob.get_P(), Bob.get_G())
print("Gen public")
print(time()-start)
Alice_Public = Alice.generate_public_key()
Bob_public = Bob.generate_public_key()
print(time()-start)
print("Gen shared")
Alice.generate_shared(Bob_public)
Bob.generate_shared(Alice_Public)
print(time()-start)
print(Alice.get_shared())
print(Bob.get_shared())
message, nonce = Alice.encrypt("Hello There")
print(message)
print(Bob.decrypt(message, nonce))
print(time()-start)
"""

