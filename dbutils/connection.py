import sqlite3


class DatabaseConnection:
    def __init__(self, **kwargs):
        self.database = kwargs.get('database', 'web-application')
        self.db = sqlite3.connect(self.database)

    def get(self):
        return self.db

    def close_connection(self):
        self.db.close()
