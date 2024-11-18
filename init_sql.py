import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='oai_user',
        password='',
        database=None  # Specify the database if needed
    )