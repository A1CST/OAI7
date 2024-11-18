import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import re
from pprint import pprint


def get_semantics_for_word(cursor, word):
    """Fetch matching semantics for a given word from Level 1 semantics table."""
    try:
        cursor.execute("""
            SELECT id, original_word, chatgpt_response_1, chatgpt_response_2, chatgpt_response_3,
                   chatgpt_response_4, chatgpt_response_5, chatgpt_response_6
            FROM OA7.level_1_semantics
            WHERE original_word = %s
        """, (word,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        return []


def get_pos_for_sentence(cursor, sentence):
    """Fetch POS data for each word in the sentence from the word_data table."""
    pos_data = {}
    words = sentence.split()  # Assuming sentence is a space-separated string
    for word in words:
        cursor.execute("""
            SELECT part_of_speech FROM OA7.word_data WHERE word = %s
        """, (word,))
        result = cursor.fetchone()
        if result:
            pos_data[word] = result[0]
        else:
            pos_data[word] = "Unknown"  # Handle cases where word is not found
    return pos_data


def get_grammar_patterns(cursor):
    """Fetch all grammar patterns from the grammar_pattern table."""
    cursor.execute("""
        SELECT pattern FROM OA7.grammar_patterns
    """)
    return [row[0] for row in cursor.fetchall()]


def check_grammar_pattern(cursor, pos_data):
    """Check the POS string against stored grammar patterns."""
    pos_string = ','.join([pos_data[word] for word in pos_data])  # Create POS string

    # Debugging: Print the POS string and the patterns
    print(f"POS Data: {pos_data}")
    print(f"Checking grammar pattern: {pos_string}")

    # Fetch patterns
    patterns = get_grammar_patterns(cursor)

    # Check for exact or partial matches
    for pattern in patterns:
        if pos_string == pattern or pos_string in pattern:
            print(f"Matching pattern found: {pattern}")
            return True  # Stop after the first match (or handle as needed)
    return False


def main():
    sentence = input("Please enter a sentence: ")
    connection = get_connection()
    cursor = connection.cursor()

    # Parse sentence and get Level 1 semantics
    words = sentence.split()
    constructed_sentence = []

    for word in words:
        print(f"Level 1 Semantics for '{word}':")
        level_1_semantics = get_semantics_for_word(cursor, word)

        if level_1_semantics:
            # For simplicity, we'll just take the first semantic match
            selected_semantic = level_1_semantics[0][2]  # Assuming chatgpt_response_1 is the desired semantic
            print(f"Constructed Sentence: {selected_semantic}")
            constructed_sentence.append(
                selected_semantic.split('=')[1].strip())  # Extract the result part of the equation

    # Construct sentence from selected semantics
    constructed_sentence_str = " ".join(constructed_sentence)

    # Get POS data for the constructed sentence
    pos_data = get_pos_for_sentence(cursor, constructed_sentence_str)

    # Check grammar pattern for the constructed sentence
    if not check_grammar_pattern(cursor, pos_data):
        print("No matching grammar patterns found.")


if __name__ == "__main__":
    main()
