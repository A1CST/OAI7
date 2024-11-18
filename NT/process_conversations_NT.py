import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import re
import time

def get_unprocessed_conversations():
    """Fetch unprocessed rows from the conversations table."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT id, gpt_response 
        FROM OA7.conversations 
        WHERE processed = 0;
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching unprocessed conversations: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def word_exists(word):
    """Check if a word exists in the word_data table and return its id and occurrence_count."""
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
    """Insert a new word into the word_data table with an initial occurrence count of 1."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO OA7.word_data (word, occurrence_count) VALUES (%s, %s)", (word, 1))
        connection.commit()
        print(f"Inserted new word: '{word}' with occurrence count 1.")
    except Error as e:
        print(f"Error inserting word '{word}': {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_word_occurrence(word_id, current_count):
    """Increment the occurrence count of an existing word."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE OA7.word_data SET occurrence_count = %s WHERE id = %s", (current_count + 1, word_id))
        connection.commit()
        print(f"Updated word ID {word_id}: New occurrence count = {current_count + 1}")
    except Error as e:
        print(f"Error updating word ID {word_id}: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def mark_conversation_as_processed(conversation_id):
    """Mark a conversation as processed."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE OA7.conversations SET processed = 1 WHERE id = %s", (conversation_id,))
        connection.commit()
        print(f"Marked conversation ID {conversation_id} as processed.")
    except Error as e:
        print(f"Error marking conversation as processed: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_gpt_response(conversation_id, response):
    """Parse the GPT response and update the word_data table accordingly."""
    words = re.findall(r'\b\w+\b', response)  # Extract individual words
    for word in words:
        existing_word = word_exists(word)
        if existing_word:
            update_word_occurrence(existing_word['id'], existing_word['occurrence_count'])
        else:
            insert_word(word)
    mark_conversation_as_processed(conversation_id)

def main():
    while True:
        print("Fetching unprocessed conversations...")
        unprocessed_conversations = get_unprocessed_conversations()
        for conversation in unprocessed_conversations:
            process_gpt_response(conversation['id'], conversation['gpt_response'])
        print("Waiting for the next cycle...")
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
