from .db import PWModel
import bcrypt
from Crypto.Protocol.KDF import PBKDF2
import base64
from Crypto.Cipher import AES
from Crypto import Random


class AuthenticationError(Exception):
    pass
class AESCrypto():
    """Code taken (and modified) from: https://www.delftstack.com/howto/python/python-aes-encryption/
    """
    def __init__(self):
        self.block_size = 16
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        
        
    def get_private_key(self,password):
        salt = b"54gdf3" # should be secret
        kdf = PBKDF2(password, salt, 64, 1000)
        key = kdf[:32]
        return key
    def encrypt(self,raw, priv_key):
        private_key = priv_key
        raw = self.pad(raw).encode('utf-8') 
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')
 
    def decrypt(self,enc, priv_key):
        private_key = priv_key
        enc = enc.encode('utf-8')
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:])).decode('utf-8')

class User():
    def __init__(self):
        self.db = PWModel()
        self.user_id = None
        self.crypter = AESCrypto()
        
    def login(self,username,password): 
        id,hash = self.db.get_user_hash_id(username)
        if bcrypt.checkpw(password.encode('utf-8'), hash):
            self.decrypt_key = self.crypter.get_private_key(password)
            self.user_id = id
        else:
            raise AuthenticationError("Password incorrect")
    def is_logged_in(func):
        """Decorator Fuction
        """
        def inner(self,*method_args, **method_kwargs):
            if self.user_id == None:
                raise AuthenticationError("No User logged in")
            result = func(self,*method_args, **method_kwargs)
            return result
        return inner
    
    def create_user(self,username,password):
        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.db.create_user(username,hash)
    def get_user_id(self):
        if self.user_id != None:
            return self.user_id
        else:
            raise AuthenticationError("No User logged in.")
    @is_logged_in
    def create_entry(self,site,username,password):
        print("Is allowed to create entry")