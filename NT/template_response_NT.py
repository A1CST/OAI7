import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import re
import time

def get_processed_conversations():
    """Fetch GPT responses from conversations where grammar_process is 0 and processed is 1."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT id, gpt_response 
        FROM OA7.conversations 
        WHERE processed = 1 AND grammar_process = 0;
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching processed conversations: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_word_id(word):
    """Fetch the word ID from the word_data table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM OA7.word_data WHERE word = %s", (word,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error fetching word ID for '{word}': {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_grammar_template(template, conversation_id):
    """Insert a new grammar template into the grammar_templates table with a conversation ID."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO OA7.grammar_templates (template, conversation_id) 
        VALUES (%s, %s);
        """, (template, conversation_id))
        connection.commit()
        print(f"Inserted grammar template: {template} for conversation ID: {conversation_id}")
    except Error as e:
        print(f"Error inserting grammar template: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def mark_conversation_as_grammar_processed(conversation_id):
    """Mark a conversation as grammar processed."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE OA7.conversations 
        SET grammar_process = 1 
        WHERE id = %s;
        """, (conversation_id,))
        connection.commit()
        print(f"Marked conversation ID {conversation_id} as grammar processed.")
    except Error as e:
        print(f"Error marking conversation as grammar processed: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_gpt_response(conversation_id, response):
    """Parse the GPT response, convert to word IDs, and save as a grammar template."""
    words = re.findall(r'\b\w+\b', response)
    word_ids = []
    for word in words:
        word_id = get_word_id(word)
        if word_id:
            word_ids.append(str(word_id))
        else:
            print(f"Word '{word}' not found in word_data table. Skipping.")

    if word_ids:
        template = " ".join(word_ids)
        insert_grammar_template(template, conversation_id)
        mark_conversation_as_grammar_processed(conversation_id)

def main():
    while True:
        print("Fetching processed conversations for grammar processing...")
        processed_conversations = get_processed_conversations()
        for conversation in processed_conversations:
            process_gpt_response(conversation['id'], conversation['gpt_response'])
        print("Waiting for the next cycle...")
        time.sleep(60)  # Run every 60 seconds

if __name__ == "__main__":
    main()
