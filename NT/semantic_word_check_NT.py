import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import re
import time

BATCH_SIZE = 100  # Define the batch size for fetching records

def get_semantics_responses(connection, cursor, batch_size=BATCH_SIZE, offset=0):
    """Fetch a batch of GPT responses from the level_1_semantics table."""
    try:
        cursor.execute(f"""
        SELECT id, chatgpt_response_1, chatgpt_response_2, chatgpt_response_3,
               chatgpt_response_4, chatgpt_response_5, chatgpt_response_6,
               chatgpt_response_7, chatgpt_response_8, chatgpt_response_9,
               chatgpt_response_10
        FROM OA7.level_1_semantics
        LIMIT {batch_size} OFFSET {offset}
        """)
        responses = cursor.fetchall()
        print(f"Fetched {len(responses)} rows from level_1_semantics table (Offset: {offset}).")
        return responses
    except Error as e:
        print(f"Error fetching semantics: {e}")
        return []

def word_exists(connection, cursor, word):
    """Check if a word exists in the word_data table."""
    try:
        cursor.execute("SELECT COUNT(*) AS count FROM OA7.word_data WHERE word = %s", (word,))
        result = cursor.fetchone()
        exists = result['count'] > 0  # Access using dictionary key
        return exists
    except Error as e:
        print(f"Error checking word existence for '{word}': {e}")
        return False

def insert_word(connection, cursor, word):
    """Insert a new word into the word_data table."""
    try:
        cursor.execute("INSERT INTO OA7.word_data (word, occurrence_count) VALUES (%s, %s)", (word, 1))
        connection.commit()
        print(f"Inserted word '{word}' into word_data table.")
    except Error as e:
        print(f"Error inserting word '{word}': {e}")

def process_gpt_responses(connection, cursor, responses):
    """Parse GPT responses, extract words, and ensure they are in the word_data table."""
    for response in responses:
        print(f"Processing row ID: {response['id']}")
        for key, value in response.items():
            if key.startswith("chatgpt_response") and value:
                words = re.findall(r'\b\w+\b', value)  # Extract words, ignore + and =
                for word in words:
                    if not word_exists(connection, cursor, word):
                        insert_word(connection, cursor, word)

def main():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        offset = 0

        while True:
            print("Starting new cycle...")
            semantics_responses = get_semantics_responses(connection, cursor, offset=offset)
            if semantics_responses:
                process_gpt_responses(connection, cursor, semantics_responses)
                offset += BATCH_SIZE
            else:
                print("No more data to process. Resetting offset.")
                offset = 0  # Reset offset when all rows are processed
            print("Waiting for 60 seconds...")
            time.sleep(300)

    except KeyboardInterrupt:
        print("Stopping process...")

    except Error as e:
        print(f"Unexpected error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()
