import uuid
import sqlite3

class GroupChatManagement:
    def __init__(self):
        self.db = 'main.db'
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS gcs(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, user_table TEXT)')
        cur.close()
        db.commit()
        db.close()
        self.invites = {}
    def create_gc(self, gc_name, username):
        gc_id = str(uuid.uuid4()).replace('-', '')
        user_table = gc_id + '_users'
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM gcs')
        data = cur.fetchall()
        for gc in data:
            if gc[1] == gc_name:
                cur.close()
                db.close()
                return 1
        cur.execute('INSERT INTO gcs VALUES(null, ?, ?)', (gc_name, user_table))
        cur.execute('CREATE TABLE {}(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)'.format(user_table))
        cur.execute('INSERT INTO {} VALUES(null, ?)'.format(user_table), (username,))
        cur.close()
        db.commit()
        db.close()
    def delete_gc(self, gc_name):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM gcs WHERE name=?', (gc_name,))
        data = cur.fetchall()
        if len(data) == 0:
            cur.close()
            db.close()
            return 1
        cur.execute('DELETE FROM gcs WHERE name=?', (gc_name,))
        cur.execute('DROP TABLE {}'.format(data[0][2]))
        cur.close()
        db.commit()
        db.close()
    def add_to_gc(self, gc_name, username):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM gcs WHERE name=?', (gc_name,))
        data = cur.fetchall()
        if len(data) == 0:
            cur.close()
            db.close()
            return 1
        cur.execute('INSERT INTO {} VALUES(null, ?)'.format(data[0][2]), (username,))
        cur.close()
        db.commit()
        db.close()
    def remove_from_gc(self, gc_name, username):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM gcs WHERE name=?', (gc_name,))
        gc_data = cur.fetchall()
        if len(gc_data) == 0:
            cur.close()
            db.close()
            return 1
        cur.execute('SELECT * FROM {} WHERE username=?'.format(gc_data[0][2]), (username,))
        user_data = cur.fetchall()
        if len(user_data) == 0:
            cur.close()
            db.close()
            return 2
        cur.execute('DELETE FROM {} WHERE username=?'.format(gc_data[0][2]), (username,))
        cur.close()
        db.commit()
        db.close()
    def get_gc_members(self, gc_name):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM gcs WHERE name=?', (gc_name,))
        data = cur.fetchall()
        if len(data) == 0:
            cur.close()
            db.close()
            return 1
        cur.execute('SELECT * FROM {}'.format(data[0][2]))
        data = cur.fetchall()
        users = []
        for user in data:
            users.append(user[1])
        cur.close()
        db.close()
        return users
    def get_gcs(self):
        db = sqlite3.connect(self.db)
        cur = db.cursor()
        cur.execute('SELECT * FROM gcs')
        data = cur.fetchall()
        gcs = []
        for gc in data:
            gcs.append(gc[1])
        cur.close()
        db.close()
        return gcs
