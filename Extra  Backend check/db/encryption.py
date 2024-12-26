from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
 
# Encryption and decryption functions
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + ciphertext).decode()

def decrypt_data(data, key):
    data = base64.b64decode(data)
    nonce = data[:16]
    ciphertext = data[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ciphertext).decode()
