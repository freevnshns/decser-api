from sqlite3 import Error

from connection import DatabaseConnection


class FileTable:
    def __init__(self):
        self.dbConnection = DatabaseConnection()

        self.NAME = "files_table"

        self.COLUMN_FILE_NAME = "file_name"
        self.COLUMN_FILE_NAME_TYPE = "varchar(250)"

        self.COLUMN_FILE_UPLOAD_DATE = "file_upload_date"
        self.COLUMN_FILE_UPLOAD_DATE_TYPE = "date"

        self.COLUMN_FILE_TYPE = "file_type"
        self.COLUMN_FILE_TYPE_TYPE = "varchar(10)"

        self.COLUMNS = "{0} {1} , {2} {3} , {4} {5} ".format(self.COLUMN_FILE_NAME, self.COLUMN_FILE_NAME_TYPE,
                                                             self.COLUMN_FILE_UPLOAD_DATE,
                                                             self.COLUMN_FILE_UPLOAD_DATE_TYPE, self.COLUMN_FILE_TYPE,
                                                             self.COLUMN_FILE_TYPE_TYPE)

        self.cursor = self.dbConnection.db.cursor()

    def create(self):
        query = "CREATE TABLE IF NOT EXISTS " + self.NAME + "\n(\n" + self.COLUMNS + "\n);"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e

    def __del__(self):
        self.dbConnection.close_connection()

    def insert(self, file_name, file_type):
        query = "INSERT INTO " + self.NAME + "(" + self.COLUMN_FILE_NAME + "," + self.COLUMN_FILE_TYPE + "," + self.COLUMN_FILE_UPLOAD_DATE + ")VALUES ('%s','%s',date('now'));" % (
            file_name, file_type)
        try:
            self.cursor.execute(query)
        except Error as e:
            if str(e) == "no such table: " + self.NAME:
                self.create()
                self.insert(file_name, file_type)
        data = self.dbConnection.get()
        data.commit()

    def get(self):
        query = "SELECT " + self.COLUMN_FILE_NAME + "," + self.COLUMN_FILE_UPLOAD_DATE + "," + self.COLUMN_FILE_TYPE + " FROM " + self.NAME + ";"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
        results = self.cursor.fetchall()
        if results:
            return results
        else:
            return []

    def remove(self, file_name):
        query = "DELETE FROM " + self.NAME + " WHERE " + self.COLUMN_FILE_NAME + "='" + file_name + "';"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
        data = self.dbConnection.get()
        data.commit()
