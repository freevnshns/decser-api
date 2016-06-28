from MySQLdb import connect


class DatabaseConnection:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', 'localhost')
        self.user = kwargs.get('user', 'root')
        self.password = kwargs.get('password', '')
        self.database = kwargs.get('database', 'HomeBase')
        self.db = connect(self.host, self.user, self.password, self.database)

    def get(self):
        return self.db

    def closeConnection(self):
        self.db.close()