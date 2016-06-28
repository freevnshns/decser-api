from MySQLdb import Error

from connection import DatabaseConnection

class usertable:
    def __init__(self):
        self.dbcon = DatabaseConnection()

        self.NAME = "usertable"

        self.COLUMN_USER_NAME = "user_name"
        self.COLUMN_USER_NAME_TYPE = "varchar(50)"

        self.COLUMN_USER_INFO = "user_info"
        self.COLUMN_USER_INFO_TYPE = "varchar(500)"

        self.COLUMNS = "{0} {1} , {2} {3} ".format(self.COLUMN_USER_NAME, self.COLUMN_USER_NAME_TYPE,
                                                   self.COLUMN_USER_INFO, self.COLUMN_USER_INFO_TYPE)

        self.cursor = self.dbcon.db.cursor()


    def create(self):
        query = "CREATE TABLE IF NOT EXISTS " + self.NAME + "\n(\n" + self.COLUMNS + "\n);"
        self.cursor.execute(query)

    def __del__(self):
        self.dbcon.closeConnection()

    def get(self, **kwargs):
        if (kwargs.get('attr') == 'user_name'):
            query = " SELECT " + self.COLUMN_USER_NAME + " FROM " + self.NAME + " ;"
        elif (kwargs.get('attr') == 'user_info'):
            query = " SELECT " + self.COLUMN_USER_INFO + " FROM " + self.NAME + " ;"
        try:
            self.cursor.execute(query)
        except Error as e:
            if e.args[0] == 1146:
                return False
        results = self.cursor.fetchall()
        for row in results:
            if row:
                return row[0]
            else:
                return 'Anonymous'
        
    def insert(self,user_name,user_info="Write something about yourself...."):
        query = "INSERT INTO " + self.NAME + "(" + self.COLUMN_USER_NAME + "," + self.COLUMN_USER_INFO +")VALUES ('%s','%s');" % (
            user_name, user_info)
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
            if e.args[0] == 1146:
                self.create()
                self.insert(user_name,user_info)
        data = self.dbcon.get()
        data.commit()

    def edit(self,user_info):
        query = "UPDATE " + self.NAME + " SET " + self.COLUMN_USER_INFO +" = '%s';" % (user_info)
        try:
            self.cursor.execute(query)
        except Error as e:
            print e
        data = self.dbcon.get()
        data.commit()
