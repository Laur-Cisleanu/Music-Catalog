import sqlite3

class Database():

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._connection = sqlite3.connect('library.db', check_same_thread=False)
            cls._instance._cursor = cls._instance._connection.cursor()
        return cls._instance
    
    def get_cursor(self):
        return self._cursor 
    
    def commit(self):
        self._connection.commit()
    
    def close(self):
        self._connection.close()
        Database._instance = None