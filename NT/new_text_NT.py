import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import time
import re

def get_unprocessed_user_inputs():
    """Fetch unprocessed rows from the user_txt_input table."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, user_input FROM OA7.user_txt_input WHERE processed = FALSE")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Error fetching user inputs: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def mark_row_as_processed(row_id):
    """Mark a row as processed in the user_txt_input table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE OA7.user_txt_input SET processed = TRUE WHERE id = %s", (row_id,))
        connection.commit()
    except Error as e:
        print(f"Error marking row {row_id} as processed: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def word_exists(word):
    """Check if a word or character already exists in the word_data table."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, occurrence_count FROM OA7.word_data WHERE word = %s", (word,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error checking word existence: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_word(word):
    """Insert a new word or character into the word_data table with initial occurrence count 1."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO OA7.word_data (word, occurrence_count) VALUES (%s, %s)", (word, 1))
        connection.commit()
    except Error as e:
        print(f"Error inserting word '{word}': {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_word_occurrence(word_id, current_count):
    """Update the occurrence count for an existing word or character."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE OA7.word_data SET occurrence_count = %s WHERE id = %s", (current_count + 1, word_id))
        connection.commit()
    except Error as e:
        print(f"Error updating occurrence count for word ID {word_id}: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_user_input(row_id, text):
    """Parse user input into words and characters, adding or updating them in the word_data table."""
    words = re.findall(r'\b\w+\b|[^\w\s]', text)  # Extract words and special characters
    for word in words:
        existing_word = word_exists(word)
        if existing_word:
            update_word_occurrence(existing_word['id'], existing_word['occurrence_count'])
        else:
            insert_word(word)
    mark_row_as_processed(row_id)

def main():
    while True:
        user_inputs = get_unprocessed_user_inputs()
        for row in user_inputs:
            process_user_input(row['id'], row['user_input'])
        print("Waiting for 3 minutes before the next check...")
        time.sleep(10)  # Wait for 3 minutes

if __name__ == "__main__":
    main()
