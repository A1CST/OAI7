import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
from functions.gpt import gpt_request_semantic  # Import the function to generate semantics
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set the number of threads for parallel processing
MAX_THREADS = 10


def get_words_without_semantics():
    """Fetch words from word_data that don't have corresponding entries in level_1_semantics as original_word."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT wd.id, wd.word 
        FROM OA7.word_data wd
        LEFT JOIN OA7.level_1_semantics s ON wd.word = s.original_word
        WHERE s.original_word IS NULL;
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching words without semantics: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def process_word(word_id, word):
    """Generate and save semantic equations for a word."""
    response_message = gpt_request_semantic(word)
    if "inserted" in response_message.lower():
        print(f"Semantics for '{word}' saved successfully.")
    else:
        print(f"Failed to generate semantics for '{word}': {response_message}")


def process_words_in_parallel(words_to_process):
    """Process words in parallel using threading."""
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(process_word, word_entry['id'], word_entry['word']): word_entry for word_entry in
                   words_to_process}

        for future in as_completed(futures):
            word_entry = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing word '{word_entry['word']}': {e}")


def main():
    while True:
        print("Fetching words without semantics...")
        words_to_process = get_words_without_semantics()

        if words_to_process:
            print(f"Processing {len(words_to_process)} words...")
            process_words_in_parallel(words_to_process)
        else:
            print("No words left to process.")

        print("Waiting for 5 minutes before the next cycle...")
        time.sleep(300)  # Check every 5 minutes


if __name__ == "__main__":
    main()
