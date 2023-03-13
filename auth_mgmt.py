import bcrypt
import sqlite3

class AuthenticationManagement:
    def __init__(self):
        self.db = 'main.db'
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, permission_level INTEGER)')
        cur.close()
        db.commit()
        db.close()
    
    def hash_passwd(self, cleartext):
        return bcrypt.hashpw(cleartext.encode(), bcrypt.gensalt())
    
    def check_passwd(self, cleartext, hashed):
        return bcrypt.checkpw(cleartext.encode(), hashed)
    
    def create_account(self, username, password, permission_level):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        for user in data:
            if user[1] == username:
                cur.close()
                db.close()
                return 1
        cur.execute('SELECT * FROM gcs')
        data = cur.fetchall()
        for gc in data:
            if gc[1] == username:
                cur.close()
                db.close()
                return 1
        password = self.hash_passwd(password).decode('utf-8')
        cur.execute('INSERT INTO users VALUES(NULL, ?, ?, ?)', (username, password, permission_level))
        cur.close()
        db.commit()
        db.close()

    def delete_account(self, username):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        found = False
        for seg in data:
            if seg[1] == username:
                found = True
        if found:
            cur.execute('DELETE FROM users WHERE username=?', (username,))
        cur.close()
        db.commit()
        db.close()
        return found

    def change_perm_level(self, username, permission_level):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        found = False
        for seg in data:
            if seg[1] == username:
                found = True
        
        if found:
            cur.execute('UPDATE users SET permission_level=? WHERE username=?', (permission_level, username))
        cur.close()
        db.commit()
        db.close()
        return found

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

    def get_perm_level(self, username):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        cur.close()
        db.close()
        permission_level = None
        for entry in data:
            if entry[1] == username:
                permission_level = entry[3]
                break
        return permission_level

    def change_password(self, username, current_password, new_password):
        logged_in = self.login(username, current_password)
        if logged_in:
            db = sqlite3.connect(self.db)
            cur = db.cursor()
            cur.execute('UPDATE users SET password=? WHERE username=?', (self.hash_passwd(new_password).decode('utf-8'), username))
            cur.close()
            db.commit()
            db.close()
        return logged_in
