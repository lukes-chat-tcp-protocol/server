import bcrypt
import sqlite3

class AuthenticationManagement:
    def __init__(self):
        self.db = 'main.db'
    
    def hash_passwd(self, cleartext):
        return bcrypt.hashpw(cleartext.encode(), bcrypt.gensalt())
    
    def check_passwd(self, cleartext, hashed):
        return bcrypt.checkpw(cleartext.encode(), hashed)
    
    def create_account(self, username, password, permission_level):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        password = self.hash_passwd(password).decode('utf-8')
        cur.execute('INSERT INTO users VALUES(NULL, ?, ?, ?)', (username, password, permission_level))
        cur.close()
        db.commit()
        db.close()

    def delete_account(self, username):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('DELETE FROM users WHERE username=?', (username,))
        cur.close()
        db.commit()
        db.close()

    def login(self, username, password):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        cur.close()
        db.close()
        login_success = False
        for entry in data:
            if entry[1] == username:
                login_success = self.check_passwd(password, entry[2].encode())
                permission_level = entry[3]
                break
        if login_success:
            return permission_level
        else:
            return False
