import mysql.connector
from mysql.connector import Error
from init_sql import get_connection

def reset_processed_columns():
    """Reset processed and grammar_process columns to 0 for conversations and grammar_templates tables."""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Reset grammar_process column in conversations table
        cursor.execute("""
        UPDATE OA7.conversations
        SET processed = 0, grammar_process = 0;
        """)
        print("Reset processed and grammar_process columns in conversations table.")

        # Reset processed column in grammar_templates table
        cursor.execute("""
        UPDATE OA7.grammar_templates
        SET processed = 0;
        """)
        print("Reset processed column in grammar_templates table.")

        connection.commit()
    except Error as e:
        print(f"Error resetting processed columns: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    reset_processed_columns()
