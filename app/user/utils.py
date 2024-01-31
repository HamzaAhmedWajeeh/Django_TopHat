from cryptography.fernet import Fernet
from datetime import datetime, timedelta
# import time

def generate_key():
    return Fernet.generate_key()

def encrypt_email(email, key):
    now = datetime.now()
    email = f"{email}--{str(now)}"
    cipher_suite = Fernet(key)
    encrypted_email = cipher_suite.encrypt(email.encode())
    return encrypted_email

def decrypt_email(encrypted_email, key):
    cipher_suite = Fernet(key)
    decrypted_email = cipher_suite.decrypt(encrypted_email).decode()
    email, time = decrypted_email.split('--')
    if (datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=15)) > datetime.now():
        return email
    else:
        return None