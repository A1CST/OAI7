import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
from functions.gpt import fetch_def_and_pos  # Import updated GPT function
import time

def get_words_missing_details():
    """Fetch words from word_data table that do not have a definition or part_of_speech."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT id, word FROM OA7.word_data 
        WHERE part_of_speech IS NULL OR part_of_speech = ''
        OR definition IS NULL OR definition = '';
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching words without details: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_word_details(word_id, definition, pos):
    """Update the definition and part_of_speech for a given word in the word_data table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE OA7.word_data 
        SET definition = %s, part_of_speech = %s 
        WHERE id = %s;
        """, (definition, pos, word_id))
        connection.commit()
        print(f"Updated word ID {word_id} with definition and POS.")
    except Error as e:
        print(f"Error updating details for word ID {word_id}: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_missing_details():
    """Process words without definitions or part of speech and update them."""
    words_to_process = get_words_missing_details()
    for word_entry in words_to_process:
        word_id = word_entry['id']
        word = word_entry['word']
        definition, pos = fetch_def_and_pos(word)
        if definition and pos:
            update_word_details(word_id, definition, pos)
        else:
            print(f"Failed to retrieve details for word: {word}")

def main():
    while True:
        print("Checking for words missing definitions or part_of_speech...")
        process_missing_details()
        print("Waiting for 15 minutes before the next check...")
        time.sleep(900)  # Wait for 15 minutes

if __name__ == "__main__":
    main()
