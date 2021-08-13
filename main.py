"""
from diffiehellman import DiffieHellman
#pip install py-diffie-hellman

# automatically generate two key pairs
dh1 = DiffieHellman(group=14, key_bits=540)
dh2 = DiffieHellman(group=14, key_bits=540)

# get both public keys
print(dh1.get_public_key())
P = int.from_bytes(dh1.get_public_key(), "big")
G = int.from_bytes(dh2.get_public_key(), "big")

#Only a or b know their respective value
a = 4
b = 3

#a and b calculate this and send the answer
A = (G**a)%P
B = (G**b)%P

#a and b calculate this which is the shaired private key
ka = (B**a)%P
kb = (A**b)%P

print("key a:"+ str(ka))
print("Key b:"+ str(ka))

"""
from key import key
Alice = key()
