from sqlite3 import Error

from connection import DatabaseConnection


class MessageTable:
    def __init__(self):
        self.dbConnection = DatabaseConnection()

        self.NAME = "messages_table"

        self.COLUMN_MESSAGE_ID = "mid"
        self.COLUMN_MESSAGE_ID_TYPE = "INT NOT NULL AUTO_INCREMENT"

        self.COLUMN_MESSAGE_DATE = "message_date"
        self.COLUMN_MESSAGE_DATE_TYPE = "date"

        self.COLUMN_MESSAGE_CATEGORY = "message_cat"
        self.COLUMN_MESSAGE_CATEGORY_TYPE = "varchar(100)"

        self.COLUMN_MESSAGE_DATA = "message_data"
        self.COLUMN_MESSAGE_DATA_TYPE = "varchar(1000)"

        self.COLUMN_MESSAGE_IP = "message_ip"
        self.COLUMN_MESSAGE_IP_TYPE = "varchar(50)"

        self.COLUMN_MESSAGE_SENDER = "message_sender"
        self.COLUMN_MESSAGE_SENDER_TYPE = "varchar(50)"

        self.COLUMNS = "{0} {1} , {2} {3} , {4} {5} , {6} {7} , {8} {9} , {10} {11}".format(self.COLUMN_MESSAGE_ID,
                                                                                            self.COLUMN_MESSAGE_ID_TYPE,
                                                                                            self.COLUMN_MESSAGE_DATE,
                                                                                            self.COLUMN_MESSAGE_DATE_TYPE,
                                                                                            self.COLUMN_MESSAGE_DATA,
                                                                                            self.COLUMN_MESSAGE_DATA_TYPE,
                                                                                            self.COLUMN_MESSAGE_IP,
                                                                                            self.COLUMN_MESSAGE_IP_TYPE,
                                                                                            self.COLUMN_MESSAGE_SENDER,
                                                                                            self.COLUMN_MESSAGE_SENDER_TYPE,
                                                                                            self.COLUMN_MESSAGE_CATEGORY,
                                                                                            self.COLUMN_MESSAGE_CATEGORY_TYPE)

        self.cursor = self.dbConnection.db.cursor()

    def __del__(self):
        self.dbConnection.close_connection()

    def create(self):
        query = "CREATE TABLE IF NOT EXISTS " + self.NAME + "\n(\n" + self.COLUMNS + ",\nPRIMARY KEY (" + self.COLUMN_MESSAGE_ID + ")\n);"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e

    def insert(self, data, ip, category, sender="Anonymous"):
        query = "INSERT INTO " + self.NAME + "(" + self.COLUMN_MESSAGE_DATA + "," + self.COLUMN_MESSAGE_IP + "," + self.COLUMN_MESSAGE_SENDER + "," + self.COLUMN_MESSAGE_DATE + "," + self.COLUMN_MESSAGE_CATEGORY + ")VALUES ('%s','%s','%s',CURDATE(),'%s');" % (
            data, ip, sender, category)
        try:
            self.cursor.execute(query)
        except Error as e:
            if e.args[0] == 1146:
                self.create()
                self.insert(data, ip, category, sender)
        data = self.dbConnection.get()
        data.commit()

    def get(self, category):
        query = "SELECT " + self.COLUMN_MESSAGE_ID + "," + self.COLUMN_MESSAGE_DATA + "," + self.COLUMN_MESSAGE_IP + "," + self.COLUMN_MESSAGE_SENDER + "," + self.COLUMN_MESSAGE_DATE + " FROM " + self.NAME + " WHERE " + self.COLUMN_MESSAGE_CATEGORY + " = '" + category + "';"
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
            return False
        results = self.cursor.fetchall()
        if results:
            return results
        else:
            return False
