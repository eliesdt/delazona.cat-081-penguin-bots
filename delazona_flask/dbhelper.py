import os
import json
import psycopg2

class DBHelper:
    def __init__(self):
        # Establishing a connection with the PostgreSQL database which is linked to Heroku
        if DEPLOYED:
            DATABASE_URL = os.environ['DATABASE_URL']
            self.conn = psycopg2.connect(DATABASE_URL,sslmode='require')

    def setup(self):
        # Creating the database (if it doesn't exist already)
        self.cur = self.conn.cursor()
        print("Creating table...")
        stmt = """CREATE TABLE IF NOT EXISTS stores (
            id TEXT,
            type TEXT,
            data json
        )"""
        self.cur.execute(stmt)
        self.conn.commit()

    def add_entry(self, id, type, data):
        # Adding an entry to the database
        stmt = """INSERT INTO stores ("id", "type", "data") VALUES (%s,%s,%s)"""
        args = (id, type, json.dumps(data))
        self.cur.execute(stmt,args)
        self.conn.commit()

    def add_result(self, id, data):
        # Adding an entry to the database
        type = "result"
        stmt = """INSERT INTO stores ("id", "type", "data") VALUES (%s,%s,%s)"""
        args = (id, type, json.dumps(data))
        self.cur.execute(stmt,args)
        self.conn.commit()

    def add_store(self, id, data):
        # Adding an entry to the database
        type = "store"
        stmt = """INSERT INTO stores ("id", "type", "data") VALUES (%s,%s,%s)"""
        args = (id, type, json.dumps(data))
        self.cur.execute(stmt,args)
        self.conn.commit()

    def add_dataset(self, id, data):
        # Adding an entry to the database
        type = "dataset"
        stmt = """INSERT INTO stores ("id", "type", "data") VALUES (%s,%s,%s)"""
        args = (id, type, json.dumps(data))
        self.cur.execute(stmt,args)
        self.conn.commit()

    def get_entry(self, id):
        # Obtaining a specific entry from the database
        stmt = """SELECT data FROM stores WHERE id = '{}'""".format(id)
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchone()[0])

    def get_result(self, id):
        # Obtaining a specific entry from the database
        stmt = """SELECT data FROM stores WHERE id = '{}' AND type = 'result'""".format(id)
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchone()[0])

    def get_results(self, id):
        # Obtaining a specific entry from the database
        stmt = """SELECT data FROM stores WHERE id = '{}' AND type = 'result'""".format(id)
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchall())

    def get_stores(self, id):
        # Obtaining a specific entry from the database
        stmt = """SELECT data FROM stores WHERE id = '{}' AND type = 'store'""".format(id)
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchall())

    def get_dataset(self, id):
        # Obtaining a specific entry from the database
        stmt = """SELECT data FROM stores WHERE id = '{}' AND type = 'dataset'""".format(id)
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchone()[0])

    def get_all_ids(self):
        # Obtaining all the entries from the database
        stmt = """SELECT id FROM stores"""
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchall())

    def get_all_entries(self):
        # Obtaining all the entries from the database
        stmt = """SELECT data FROM stores"""
        self.cur.execute(stmt)
        return json.dumps(self.cur.fetchall())

    def delete_duplicate_entries(self):
        stmt = """DELETE FROM stores a WHERE a.ctid <> (SELECT min(b.ctid) FROM stores b WHERE a.id = b.id)"""
        self.cur.execute(stmt)
        self.conn.commit()

    def update_entry(self, id, type, data):
        stmt = """UPDATE stores SET data = %s, type = %s WHERE id = %s"""
        args = (json.dumps(data),type, id)
        self.cur.execute(stmt,args)
        self.conn.commit()

    def delete_entry(self, id):
        stmt = """DELETE FROM stores WHERE id = '{}'""".format(id)
        self.cur.execute(stmt)
        self.conn.commit()
