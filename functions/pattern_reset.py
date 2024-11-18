import mysql.connector
from mysql.connector import Error
from init_sql import get_connection

def reset_patterns_table():
    """Reset the processed column in the patterns table to 0."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE OA7.patterns SET processed = 0;")
        connection.commit()
        print("All rows in the patterns table have been reset.")
    except Error as e:
        print(f"Error resetting patterns table: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    reset_patterns_table()
