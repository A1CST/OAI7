"MUST RUN, its on loop every 5 minutes"

import sys
import mysql.connector
from mysql.connector import Error
from init_sql import get_connection


def ensure_user_txt_input_table():
    """Ensure the user_txt_input table exists in the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.user_txt_input (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_input TEXT NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
                """)
        connection.commit()
    except Error as e:
        print(f"Error ensuring table existence: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def sanitize_input(user_input):
    """Sanitize the user input to prevent SQL injection."""
    return user_input.replace("'", "''")


def insert_user_input(user_input):
    """Insert sanitized user input into the user_txt_input table."""
    sanitized_input = sanitize_input(user_input)
    query = "INSERT INTO OA7.user_txt_input (user_input) VALUES (%s)"

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (sanitized_input,))
        connection.commit()
        print("Input saved successfully.")
    except Error as e:
        print(f"Error inserting user input: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    if len(sys.argv) < 2:
        print("No input provided.")
        return

    user_input = ' '.join(sys.argv[1:])  # Combine all command-line arguments as a single input
    ensure_user_txt_input_table()
    insert_user_input(user_input)
    print("User input processed and saved.")


if __name__ == "__main__":
    main()
