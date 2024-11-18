import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import openai  # Ensure OpenAI API is properly configured
import random
import time


def get_random_words(limit=5):
    """Fetch a random set of words from the word_data table."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT word FROM OA7.word_data ORDER BY RAND() LIMIT {limit}")
        words = cursor.fetchall()
        return [word['word'] for word in words]
    except Error as e:
        print(f"Error fetching random words: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def gpt_generate_response(oai_sentence):
    """Call GPT API to generate a conversational response using Chat Completions API."""
    system_message = (
        "You are a conversational assistant. Use 2-3 words from the given input sentence to generate a proper conversational response and continue the dialogue. The words might seem random becuase they are, help build this AI's foundational langauge skills by providing feedback and conversational experience"
    )
    full_prompt = f"Input: {oai_sentence}\nGenerate a response using 2-3 words from the input."

    try:
        client = openai.OpenAI()  # Using your defined client structure
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Replace this with your desired model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ]
        )

        # Extract and return the response content
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating GPT response: {e}")
        return None


def insert_conversation(oai_sentence, gpt_response):
    """Insert a new conversation into the conversations table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO OA7.conversations (OAI_response, gpt_response) 
        VALUES (%s, %s);
        """, (oai_sentence, gpt_response))
        connection.commit()
        print(f"Inserted conversation: OAI: '{oai_sentence}' | GPT: '{gpt_response}'")
    except Error as e:
        print(f"Error inserting conversation: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def generate_conversation():
    """Generate a conversation using random words and GPT."""
    words = get_random_words()
    if words:
        oai_sentence = " ".join(words)
        print(f"OAI Sentence: {oai_sentence}")

        gpt_response = gpt_generate_response(oai_sentence)
        if gpt_response:
            insert_conversation(oai_sentence, gpt_response)
        else:
            print("Failed to generate GPT response.")


def main():
    while True:
        generate_conversation()
        time.sleep(3)  # Wait for 3 seconds


if __name__ == "__main__":
    main()
