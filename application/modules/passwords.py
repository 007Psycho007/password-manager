from ast import Pass
from re import U
from .db import PWModel
import bcrypt
from Crypto.Protocol.KDF import PBKDF2
import base64
from Crypto.Cipher import AES
from Crypto import Random
from tabulate import tabulate
import string
import random
import requests

class ManagerError(Exception):
    pass
class AuthenticationError(ManagerError):
    pass
class NotLoggedInError(ManagerError):
    pass
class ValidationError(ManagerError):
    pass


class AESCrypto():
    """Code taken (and modified) from: https://www.delftstack.com/howto/python/python-aes-encryption/
    """
    def __init__(self):
        self.block_size = 16
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        
        
    def get_private_key(self,password: str) -> bytes:
        """Generates a Private Key through the entry of a password

        Args:
            password (str): Password String

        Returns:
            bytes: Private Key as bytes object
        """
        salt = b"54gdf3" # should be secret
        kdf = PBKDF2(password, salt, 64, 1000)
        key = kdf[:32]
        return key
    def encrypt(self,raw: str, priv_key: bytes) -> str:
        """Encrypts a String with AES

        Args:
            raw (str): Raw String to encrypt
            priv_key (bytes): Private Key as bytes object.

        Returns:
            str: Encrypted String
        """
        private_key = priv_key
        raw = self.pad(raw).encode('utf-8') 
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')
 
    def decrypt(self,enc: str, priv_key: bytes) -> str:
        """Decrypts an encrypted string.

        Args:
            enc (str): Encrypted String which has been encrypted with the provided private key
            priv_key (bytes): Private Key as bytes object.

        Returns:
            str: Decrypted String
        """
        private_key = priv_key
        enc = enc.encode('utf-8')
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:])).decode('utf-8')

class Manager():
    """Class to handle the User interaction and the database operations
    """
    def __init__(self):
        self.db = PWModel()
        self.user_id = None
        self.user_name = None
        self.__priv_key = None
        self.crypter = AESCrypto()
        
    def __repr__(self):
        if self.user_name == None:
            return f"Password-Manager Object: No User logged in"
        else: 
            return f"Password-Manager Object: {self.user_name} logged in"
        
    def is_logged_in(func):
        """Decorator Fuction to check if a User is logged in.
        """
        def inner(self,*method_args, **method_kwargs):
            if self.user_id == None:
                raise NotLoggedInError("No User logged in")
            result = func(self,*method_args, **method_kwargs)
            return result
        return inner
    
    def login(self,username: str,password: str) -> None: 
        """Login a user

        Args:
            username (str): username
            password (str): password

        Raises:
            AuthenticationError: Raises Error if Authentication fails
        """
        id,hash = self.db.get_user_hash_id(username)
        if bcrypt.checkpw(password.encode('utf-8'), hash):
            self.__priv_key = self.crypter.get_private_key(password)
            self.user_id = id
            self.user_name = username
        else:
            raise AuthenticationError("Password incorrect")
     
    @classmethod
    def generate_password(cls,num=True,low=True,upp=True,sym=True,length=16,online=True):
        all= ""
        if num:
            all += string.digits
        if low:
            all += string.ascii_lowercase
        if upp:
            all += string.ascii_uppercase
        if sym:
            all += string.punctuation
        if online:
            try:
                random.seed(int(requests.get("https://www.random.org/integers/?num=1&min=1000&max=9999&col=5&base=10&format=plain&rnd=new").text))
            except (requests.Timeout,requests.ConnectionError):
                pass
        return "".join(random.sample(all,length))
    
    @classmethod
    def validate_password(cls,passwd):
        if len(passwd) < 6:
            raise ValidationError("Password should be at least 8 Characters long")
        if len(passwd) > 50:
            raise ValidationError("Password is too long")
        if not any(char.isdigit() for char in passwd):
            raise ValidationError("Password has no numbers")
        if not any(char.isupper() for char in passwd):
            raise ValidationError("Password has no uppercase letters")
        if not any(char.islower() for char in passwd):
            raise ValidationError("Password has no lowercase letters")
        if not any(char in string.punctuation for char in passwd):
            raise ValidationError("Password has no Special Characters")
        return True
    
    
    def create_user(self,username: str,password: str,confirm: str) -> None:
        """Creates a new user

        Args:
            username (str): username
            password (str): password
        """
        if not bool(username):
            raise ValidationError("No Username entered")
        if password != confirm:
            raise ValidationError("Passwords do not match")
        self.validate_password(password)
        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=14))
        self.db.create_user(username,hash)

    def get_user_id(self) -> int:
        """Get the user ID if logged in

        Raises:
            AuthenticationError: Raises if no user is logged in

        Returns:
            int: User ID
        """
        if self.user_id != None and self.priv_key != None:
            return self.user_id
        else:
            raise AuthenticationError("No User logged in.")
        

    
    @is_logged_in
    def create_entry(self,site,username,password) -> None:
        hash = self.crypter.encrypt(password,self.__priv_key)
        self.db.create_entry(site,username,hash,self.user_id)
        
    @is_logged_in
    def edit_entry(self,id,site,username,password) -> None:
        hash = self.crypter.encrypt(password,self.__priv_key)
        self.db.edit_entry(id,site,username,hash,self.user_id)
        
    @is_logged_in
    def get_all_entries(self):
        return self.db.get_all_entries(self.user_id)
    
    @is_logged_in
    def get_single_entry_id(self,id):
        data = list(self.db.get_single_entry(id,self.user_id))
        data[2] = self.crypter.decrypt(data[2],self.__priv_key)
        return data
    
    @is_logged_in
    def get_site(self,id):
        return self.db.get_entry_site(id)[0]
    
    @is_logged_in
    def get_username(self,id):
        return self.db.get_entry_username(id)[0]
    
    @is_logged_in
    def get_password(self,id):
        hash = self.db.get_entry_hash(id,self.user_id)[0]
        password = self.crypter.decrypt(hash,self.__priv_key)
        return password
    
    @is_logged_in
    def delete_entry(self,id):
        self.db.delete_entry(id)
        
    @is_logged_in
    def logout(self):
        self.user_id = None
        self.user_name = None
        self.__priv_key = None