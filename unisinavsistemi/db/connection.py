import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return conn
    except Error as e:
        print("Veritabanına bağlanırken hata oluştu:", e)
        raise
