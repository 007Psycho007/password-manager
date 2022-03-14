import sqlite3 as lite
from typing import Tuple

class PWModelError(Exception):
    pass
class UserAlreadyExists(PWModelError):
    pass
class UserDoesNotExist(PWModelError):
    pass
class EntryAlreadyExists(PWModelError):
    pass
class EntryDoesNotExists(PWModelError):
    pass

class PWModel():
    def __init__(self) -> None:
        self.conn = lite.connect("db/passwords.sqlite")
        self.cursor = self.conn.cursor()
        self.create_model()

    def __del__(self) -> None:
        self.conn.close()
        
    def create_model(self) -> None:
        """
        Generate the Datbasemodel
        """
        query = "CREATE TABLE IF NOT EXISTS master(ID INTEGER PRIMARY KEY AUTOINCREMENT,username varchar(255),hash varchar(255))"
        self.cursor.execute(query)
        self.conn.commit()
        query = "CREATE TABLE IF NOT EXISTS passwords(ID INTEGER PRIMARY KEY AUTOINCREMENT,site varchar(255),username varchar(255),hash varchar(255),master_ID INTEGER,FOREIGN KEY(master_ID) REFERENCES master(ID))"
        self.cursor.execute(query)
        self.conn.commit()

    def create_user(self,username: str,hash: str) -> None:
        """Create a new User in the Master Table

        Args:
            username (str): Username
            hash (str): A already hashed password.

        Raises:
            UserAlreadyExists: Return Error if User already exists
        """
        query = "SELECT True FROM master WHERE username=?"
        if self.cursor.execute(query,(username,)).fetchone() != None:
            raise UserAlreadyExists(f"{username} already exists.")
        query = "INSERT INTO master(username,hash) VALUES(?,?)"
        self.cursor.execute(query, (username,hash))
        self.conn.commit()
        
    def get_user_hash_id(self,username: str)-> Tuple:
        """Returns the Passwordhash and the User ID from the username

        Args:
            username (str): Username

        Raises:
            UserDoesNotExist: Return Error when User does not exist

        Returns:
            Tuple: Tuple containing the ID and the hash
        """
        query = "SELECT ID,hash FROM master WHERE username=?"
        data = self.cursor.execute(query, (username,)).fetchone()
        if data == None:
            raise UserDoesNotExist(f"{username} does not exist")
        else:
            return data
        
    def create_entry(self,site,username,hash,user_id):
        query = "SELECT True FROM passwords WHERE site=? AND username=? AND master_ID=?"
        if self.cursor.execute(query,(site,username,user_id)).fetchone() != None:
            raise EntryAlreadyExists(f"{site} with username {username} already exists.")
        query = "INSERT INTO passwords(site,username,hash,master_ID) VALUES(?,?,?,?)"
        self.cursor.execute(query, (site,username,hash,user_id))
        self.conn.commit()
        
    def edit_entry(self,id,site,username,hash,user_id):
        query = "SELECT True FROM passwords WHERE id=?"
        if self.cursor.execute(query,(id,)).fetchone() == None:
            raise EntryDoesNotExists(f"No Entry found")
        query = "UPDATE passwords SET site=?,username=?,hash=?,master_ID=? WHERE ID=?"
        self.cursor.execute(query, (site,username,hash,user_id,id))
        self.conn.commit()

    def get_all_entries(self, user_id):
        query = "SELECT ID,site,username FROM passwords WHERE master_ID=?"
        return self.cursor.execute(query,(user_id,)).fetchall()
    
    def get_entry_site(self,id):
        query = "SELECT site FROM passwords WHERE ID=?"
        return self.cursor.execute(query,(id,)).fetchone()
    
    def get_entry_username(self,id):
        query = "SELECT username FROM passwords WHERE ID=?"
        return self.cursor.execute(query,(id,)).fetchone()
    
    def get_entry_password(self,id):
        query = "SELECT hash FROM passwords WHERE ID=?"
        return self.cursor.execute(query,(id,)).fetchone()
    
    def get_single_entry(self,id,user_id):
        query = "SELECT site,username,hash FROM passwords WHERE ID=? AND master_ID=?"
        data = self.cursor.execute(query,(id,user_id)).fetchone()
        if data == None:
            raise EntryDoesNotExists(f"No Entry found")
        else:
            return data
    
    def get_entry_hash(self,id,user_id):
        query = "SELECT hash FROM passwords WHERE ID=? AND master_ID=?"
        data = self.cursor.execute(query,(id,user_id)).fetchone()
        if data == None:
            raise EntryDoesNotExists(f"No Entry found")
        else:
            return data
        
    def delete_entry(self,id):
        query = "DELETE FROM passwords WHERE ID=?"
        self.cursor.execute(query, (id,))
        self.conn.commit()