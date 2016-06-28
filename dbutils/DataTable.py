from sqlite3 import Error

from connection import DatabaseConnection


class DataTable:
    def __init__(self):
        self.dbConnection = DatabaseConnection()

        self.NAME = "data_table"

        self.COLUMN_INITIALIZED = "initialized"
        self.COLUMN_INITIALIZED_TYPE = "INT"

        self.COLUMNS = "{0} {1} ".format(self.COLUMN_INITIALIZED, self.COLUMN_INITIALIZED_TYPE)

        self.cursor = self.dbConnection.db.cursor()

    def create(self):
        query = "CREATE TABLE IF NOT EXISTS " + self.NAME + "\n(\n" + self.COLUMNS + "\n);"
        self.cursor.execute(query)

    def set_initialization(self, status):
        query = "UPDATE " + self.NAME + " SET " + self.COLUMN_INITIALIZED + " = " + str(status) + ";"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e

    def is_initialized(self):
        query = "SELECT " + self.COLUMN_INITIALIZED + " FROM " + self.NAME + ";"
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result == 0:
                return False
            else:
                return True
        except Error as e:
            if str(e) == "no such table: " + self.NAME:
                self.create()
                self.set_initialization(0)

    def __del__(self):
        self.dbConnection.close_connection()
