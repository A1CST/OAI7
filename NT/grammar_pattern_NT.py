import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import re
import time

BATCH_SIZE = 50  # Process patterns in smaller batches

def get_patterns(cursor, batch_size=BATCH_SIZE):
    """Fetch a batch of unprocessed patterns from the patterns table."""
    try:
        cursor.execute(f"""
        SELECT id, pattern 
        FROM OA7.patterns
        WHERE processed = 0
        LIMIT {batch_size};
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching patterns: {e}")
        return []

def get_pos_for_word_id(cursor, word_id):
    """Fetch the part of speech for a given word ID."""
    try:
        cursor.execute("""
        SELECT part_of_speech 
        FROM OA7.word_data 
        WHERE id = %s
        """, (word_id,))
        result = cursor.fetchone()
        return result['part_of_speech'] if result else None
    except Error as e:
        print(f"Error fetching POS for word ID {word_id}: {e}")
        return None

def insert_or_update_grammar_pattern(cursor, pos_pattern):
    """Insert or update a POS pattern in the grammar_patterns table."""
    try:
        cursor.execute("""
        SELECT id, occurrence_count 
        FROM OA7.grammar_patterns 
        WHERE pattern = %s
        """, (pos_pattern,))
        result = cursor.fetchone()

        if result:
            # Pattern exists, update occurrence count
            pattern_id = result['id']
            occurrence_count = result['occurrence_count']
            cursor.execute("""
            UPDATE OA7.grammar_patterns 
            SET occurrence_count = %s 
            WHERE id = %s
            """, (occurrence_count + 1, pattern_id))
            print(f"Updated occurrence count for pattern: {pos_pattern}")
        else:
            # Pattern does not exist, insert new record
            cursor.execute("""
            INSERT INTO OA7.grammar_patterns (pattern) 
            VALUES (%s)
            """, (pos_pattern,))
            print(f"Inserted new grammar pattern: {pos_pattern}")
    except Error as e:
        print(f"Error inserting or updating grammar pattern: {e}")

def mark_pattern_as_processed(cursor, pattern_id):
    """Mark a pattern as processed in the patterns table."""
    try:
        cursor.execute("""
        UPDATE OA7.patterns 
        SET processed = 1 
        WHERE id = %s
        """, (pattern_id,))
        print(f"Marked pattern ID {pattern_id} as processed.")
    except Error as e:
        print(f"Error marking pattern as processed: {e}")

def process_patterns():
    """Main loop to process patterns and convert them to POS patterns."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        while True:
            print("Fetching unprocessed patterns...")
            patterns = get_patterns(cursor)

            if not patterns:
                print("No unprocessed patterns found. Waiting...")
                time.sleep(60)
                continue

            for pattern_entry in patterns:
                pattern_id = pattern_entry['id']
                pattern = pattern_entry['pattern']
                word_ids = re.findall(r'\d+', pattern)

                pos_pattern = []
                skip_pattern = False

                for word_id in word_ids:
                    pos = get_pos_for_word_id(cursor, word_id)
                    if pos:
                        pos_pattern.append(pos)
                    else:
                        print(f"POS not found for word ID {word_id}, skipping pattern.")
                        skip_pattern = True
                        break

                if not skip_pattern:
                    pos_pattern_str = ", ".join(pos_pattern)
                    insert_or_update_grammar_pattern(cursor, pos_pattern_str)

                mark_pattern_as_processed(cursor, pattern_id)

            connection.commit()  # Commit changes after processing each batch
            print("Batch processed. Waiting for the next cycle...")
            time.sleep(5)

    except Error as e:
        print(f"Error during processing: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    process_patterns()
