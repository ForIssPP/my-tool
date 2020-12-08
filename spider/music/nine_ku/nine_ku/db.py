import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_DATABASE = 'nineku_music'


class DB:
    connect = pymysql.connect(
        DB_HOST,
        DB_USER,
        DB_PASSWORD,
        DB_DATABASE
    )
    cursor = connect.cursor()
