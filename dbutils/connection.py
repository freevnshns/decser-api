import os
import sqlite3


class DatabaseConnection:
    def __init__(self):
        self.database = os.path.join(os.environ.get('IHS_DATA_DIR'), 'ihs.db')
        self.db = sqlite3.connect(self.database)

    def get(self):
        return self.db

    def close_connection(self):
        self.db.close()
