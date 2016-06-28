from MySQLdb import Error

from connection import DatabaseConnection


class chat_table:
    def __init__(self):
        self.dbcon = DatabaseConnection()

        self.NAME = "chat_table"

        self.COLUMN_MESSAGE_SENDER = "message_sender"
        self.COLUMN_MESSAGE_SENDER_TYPE = "VARCHAR(50)"

        self.COLUMN_MESSAGE_DATA = "message_data"
        self.COLUMN_MESSAGE_DATA_TYPE = "VARCHAR(500)"

        self.COLUMN_MESSAGE_DATE = "message_date"
        self.COLUMN_MESSAGE_DATE_TYPE = "DATE"

        self.COLUMN_MESSAGE_TIME = "message_time"
        self.COLUMN_MESSAGE_TIME_TYPE = "TIME"

        self.COLUMNS = "{0} {1} , {2} {3} , {4} {5} , {6} {7} ".format(self.COLUMN_MESSAGE_SENDER,
                                                             self.COLUMN_MESSAGE_SENDER_TYPE, self.COLUMN_MESSAGE_DATA,
                                                             self.COLUMN_MESSAGE_DATA_TYPE, self.COLUMN_MESSAGE_DATE,
                                                             self.COLUMN_MESSAGE_DATE_TYPE, self.COLUMN_MESSAGE_TIME,
                                                             self.COLUMN_MESSAGE_TIME_TYPE)
        self.cursor = self.dbcon.db.cursor()

    def create(self):
        query = "CREATE TABLE IF NOT EXISTS " + self.NAME + "\n(\n" + self.COLUMNS + "\n);"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e

    def __del__(self):
        self.dbcon.closeConnection()

    def insert(self, message, sender="Anonymous"):
        query = "INSERT INTO " + self.NAME + "(" + self.COLUMN_MESSAGE_DATA + "," + self.COLUMN_MESSAGE_SENDER + "," + self.COLUMN_MESSAGE_DATE+","+self.COLUMN_MESSAGE_TIME + ")VALUES ('%s','%s',CURDATE(),CURTIME());" % (
            message, sender)
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
            if e.args[0] == 1146:
                self.create()
                self.insert(message, sender)
        data = self.dbcon.get()
        data.commit()

    def get(self):
        query = "SELECT " + self.COLUMN_MESSAGE_SENDER + "," + self.COLUMN_MESSAGE_DATE + "," + self.COLUMN_MESSAGE_TIME + ',' + self.COLUMN_MESSAGE_DATA + " FROM (" + "SELECT " + self.COLUMN_MESSAGE_SENDER + "," + self.COLUMN_MESSAGE_DATE + ',' + self.COLUMN_MESSAGE_TIME + "," + self.COLUMN_MESSAGE_DATA + " FROM " + self.NAME + " ORDER BY " + self.COLUMN_MESSAGE_DATE + ',' + self.COLUMN_MESSAGE_TIME + " ASC ) sub ORDER BY " + self.COLUMN_MESSAGE_DATE + ',' + self.COLUMN_MESSAGE_TIME + " ASC;"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
            if e.args[0] == 1146:
                self.create()

        results = self.cursor.fetchall()
        if results:
            return results
        else:
            return False