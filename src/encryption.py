# src/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def generate_key(password, salt=None):
    if not salt:
        salt = os.urandom(16)
    password = password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key, salt

def create_cipher(key):
    return Fernet(key)

def encrypt_file(file_path, cipher):
    with open(file_path, 'rb') as f:
        file_data = f.read()
    encrypted_data = cipher.encrypt(file_data)
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)

def decrypt_file(file_path, cipher):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data  # Not: Bu fonksiyon, veriyi döndürüyor (paylaştığınız kasa.py buna uygun)