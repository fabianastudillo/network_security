#!/usr/bin/env python3

# Reference: https://medium.com/@sadatnazrul/diffie-hellman-key-exchange-explained-python-8d67c378701c

class DH_Endpoint(object):
    def __init__(self, public_key1, public_key2, private_key):
        self.public_key1 = public_key1
        self.public_key2 = public_key2
        self.private_key = private_key
        self.full_key = None
        
    def generate_partial_key(self):
        partial_key = self.public_key1**self.private_key
        partial_key = partial_key%self.public_key2
        return partial_key
    
    def generate_full_key(self, partial_key_r):
        full_key = partial_key_r**self.private_key
        full_key = full_key%self.public_key2
        self.full_key = full_key
        return full_key
    
    def encrypt_message(self, message):
        encrypted_message = ""
        key = self.full_key
        for c in message:
            encrypted_message += chr(ord(c)+key)
        return encrypted_message
    
    def decrypt_message(self, encrypted_message):
        decrypted_message = ""
        key = self.full_key
        for c in encrypted_message:
            decrypted_message += chr(ord(c)-key)
        return decrypted_message

mensaje="Este es el mensaje secreto !!!"
bob_public=197
bob_private=199
alice_public=151
alice_private=157
Bob = DH_Endpoint(bob_public, alice_public, bob_private)
Alice = DH_Endpoint(bob_public, alice_public, alice_private)

bob_partial=Bob.generate_partial_key()
print(bob_partial)

alice_partial=Alice.generate_partial_key()
print(alice_partial)

bob_full=Bob.generate_full_key(alice_partial)
print(bob_full)

alice_full=Alice.generate_full_key(bob_partial)
print(alice_full)

m_encriptado=Alice.encrypt_message(mensaje)
print(m_encriptado)

mensajeDesencriptado = Bob.decrypt_message(m_encriptado)
print(mensajeDesencriptado)