import mysql.connector
from init_sql import get_connection
from mysql.connector import Error

def reset_higher_semantic():
    """Reset the higher_semantic column to 0 for all rows in level_1_semantics table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE OA7.level_1_semantics
        SET higher_semantic = 0;
        """)
        connection.commit()
        print("Successfully reset the higher_semantic column.")
    except Error as e:
        print(f"Error resetting higher_semantic column: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    reset_higher_semantic()
