from cryptography.fernet import Fernet
from dbdash.config import Config
import base64 

def EncValue(inputValue):
    key = Config.SECRET_KEY.encode()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    return fernet.encrypt(inputValue.encode())

def DecryptValue(inputValue):
    key = Config.SECRET_KEY.encode()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    return fernet.decrypt(inputValue).decode()