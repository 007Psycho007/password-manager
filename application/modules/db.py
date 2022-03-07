import sqlite3 as lite

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
        query = "CREATE TABLE IF NOT EXISTS master(ID INTEGER PRIMARY KEY AUTOINCREMENT,username varchar(255),hash varchar(255))"
        self.cursor.execute(query)
        self.conn.commit()
        query = "CREATE TABLE IF NOT EXISTS passwords(ID INTEGER PRIMARY KEY AUTOINCREMENT,site varchar(255),username varchar(255),hash varchar(255),master_ID INTEGER,FOREIGN KEY(master_ID) REFERENCES master(ID))"
        self.cursor.execute(query)
        self.conn.commit()

    def create_user(self,username: str,hash: str) -> None:
        query = "SELECT True FROM master WHERE username=?"
        if self.cursor.execute(query,(username,)).fetchone() != None:
            raise UserAlreadyExists(f"{username} already exists.")
        query = "INSERT INTO master(username,hash) VALUES(?,?)"
        self.cursor.execute(query, (username,hash))
        self.conn.commit()
        
    def get_user_hash_id(self,username):
        query = "SELECT ID,hash FROM master WHERE username=?"
        hash = self.cursor.execute(query, (username,)).fetchone()
        if hash == None:
            raise UserDoesNotExist(f"{username} does not exist")
        else:
            return hash
        
    def create_entry(self,site,username,hash,user_id):
        query = "SELECT True FROM passwords WHERE site=? AND username=?"
        if self.cursor.execute(query,(site,username)).fetchone() != None:
            raise EntryAlreadyExists(f"{site} with username {username} already exists.")
        query = "INSERT INTO passwords(site,username,hash,master_ID) VALUES(?,?,?,?)"
        self.cursor.execute(query, (site,username,hash,user_id))
        self.conn.commit()
        
    def get_all_entries(self, user_id):
        query = "SELECT ID,site,username FROM passwords WHERE master_ID=?"
        return self.cursor.execute(query,(user_id,)).fetchall()
    
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
        
    def delete_entry(self,id):
        query = "DELETE FROM passwords WHERE ID=?"
        self.cursor.execute(query, (id,))
        self.conn.commit()