import sqlite3 as lite

class UserModelError(Exception):
    pass
class UserAlreadyExists(UserModelError):
    pass
class UserDoesNotExist(UserModelError):
    pass

class PWModel():
    def __init__(self):
        self.conn = lite.connect("db/passwords.sqlite")
        self.cursor = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()
    def create_model(self):
        query = "CREATE TABLE IF NOT EXISTS master(ID INTEGER PRIMARY KEY AUTOINCREMENT,username varchar(255),hash varchar(255))"
        self.cursor.execute(query)
        self.conn.commit()
        query = "CREATE TABLE IF NOT EXISTS passwords(ID INTEGER PRIMARY KEY AUTOINCREMENT,site varchar(255),username varchar(255),password varchar(255),master_ID INTEGER,FOREIGN KEY(master_ID) REFERENCES master(ID))"
        self.cursor.execute(query)
        self.conn.commit()

    def create_user(self,username,hash):
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
        
