import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_DATABASE = 'onekmn'


class CreateMysqlConnector:
    def __init__(self):
        self.connect = pymysql.connect(
            DB_HOST,
            DB_USER,
            DB_PASSWORD,
            DB_DATABASE
        )
        self.cursor = self.connect.cursor()

    def create_table(self, table_name, *columns):
        table_exits = False

        self.cursor.execute('SHOW TABLES')

        for name in self.cursor:
            if table_name in name:
                table_exits = True

        if not table_exits:
            self.cursor.execute(f'CREATE TABLE {table_name} ({",".join(columns)})')
            self.cursor.fetchall()
