import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import openai  # Ensure OpenAI API is properly configured
import random
import time


def get_random_words():
    """Fetch a random set of words from the word_data table based on occurrence and POS."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Query to get words and their parts of speech
        cursor.execute("""
            SELECT word, part_of_speech
            FROM OA7.word_data
        """)
        words = cursor.fetchall()

        # Randomize the number of words to select (between 1 and 30)
        limit = random.randint(1, 30)

        # Shuffle words to randomize the selection
        random.shuffle(words)

        selected_words = []
        last_pos = None  # To ensure we don't pick two words with the same POS consecutively

        for word in words:
            if len(selected_words) < limit and (last_pos is None or word['part_of_speech'] != last_pos):
                selected_words.append(word['word'])
                last_pos = word['part_of_speech']  # Update the last_pos to current word's POS

            if len(selected_words) >= limit:  # Stop once we've selected the desired number of words
                break

        # Join selected words into a string and pass it to the GPT function
        selected_words_string = ' '.join(selected_words)

        print(f"Selected Words: {selected_words_string}")  # Debug: Show the selected words
        corrected_sentence = gpt_generate_response(selected_words_string)
        print(corrected_sentence)
        insert_conversation(selected_words_string, corrected_sentence)

    except Error as e:
        print(f"Error fetching random words: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def gpt_generate_response(oai_sentence):
    """Call GPT API to generate a conversational response using Chat Completions API."""
    system_message = (
        "You are creating an AI that is learning by chatting. Most messages will be random words; choose a few words from the message and construct a sentence to carry a conversation."
    )
    full_prompt = f"Input: {oai_sentence}\nGenerate a response using 10% of the words from the input to create a sentence that still makes sense."

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
        gpt_response = response.choices[0].message.content.strip()

        # Check if GPT response includes approximately 10% of the words from input
        input_word_count = len(oai_sentence.split())
        gpt_word_count = len(gpt_response.split())

        if gpt_word_count < input_word_count * 0.1:
            print(
                f"Warning: GPT response uses less than 10% of the words. Response length: {gpt_word_count}/{input_word_count}")

        return gpt_response
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
