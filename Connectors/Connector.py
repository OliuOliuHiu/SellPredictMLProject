import pymysql
import pandas as pd

class Connector:
    def __init__(self, server=None, port=None, database=None, username=None, password=None):
        self.server = server or 'localhost'
        self.port = port or 3306
        self.database = database or 'pizzamanager'
        self.username = username or 'root'
        self.password = password or '123456'
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.server,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor  # Trả về dictionary giống mysql.connector
            )
            self.cursor = self.conn.cursor()
            print("Successfully connected to MySQL database")
            return self.cursor
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def queryDataset(self, sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                return pd.DataFrame(result)
            return None
        except pymysql.MySQLError as e:
            print(f"Error executing query: {e}")
            return None

    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                print("🔌 MySQL connection closed.")
        except:
            pass
