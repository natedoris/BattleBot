import sqlite3

class DB():

    def __init__(self):
        PATH = "db\\auth.db"
        self.conn = sqlite3.connect(PATH)
        self.cursor = self.conn.cursor()