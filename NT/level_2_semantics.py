import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
from functions.gpt import second_level_gpt_semantics  # Assume this prompts GPT for higher-level concepts
import time

def get_level_1_semantics():
    """Fetch Level 1 semantic equations from the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT id, chatgpt_response_1, chatgpt_response_2, chatgpt_response_3,
               chatgpt_response_4, chatgpt_response_5, chatgpt_response_6,
               chatgpt_response_7, chatgpt_response_8, chatgpt_response_9,
               chatgpt_response_10
        FROM OA7.level_1_semantics
        WHERE higher_semantic = 0;
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching Level 1 semantics: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_level_2_semantics(row):
    """Combine responses from a single Level 1 semantic row into a higher-level equation."""
    combined_elements = []
    source_equations = []

    for key, value in row.items():
        if key.startswith("chatgpt_response") and value:
            result_part = value.split('=')[-1].strip()  # Extract result part
            combined_elements.append(result_part)
            source_equations.append(f"{value.strip()} (from ID: {row['id']})")

    if len(combined_elements) >= 2:
        combined_str = " + ".join(combined_elements[:4])  # Limit to 4 elements
        result = second_level_gpt_semantics(combined_str)
        return combined_str, result, source_equations

    return None, None, []

def save_level_2_semantics(combined, result, source_equations, parent_id):
    """Save Level 2 semantics into the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO OA7.level_2_semantics (combined_elements, result, source_equations, parent_id)
        VALUES (%s, %s, %s, %s);
        """, (combined, result, "; ".join(source_equations), parent_id))
        cursor.execute("""
        UPDATE OA7.level_1_semantics
        SET higher_semantic = 1
        WHERE id = %s;
        """, (parent_id,))
        connection.commit()
        print(f"[DEBUG] Saved Level 2 Semantic: {combined} = {result}")
    except Error as e:
        print(f"Error saving Level 2 semantics: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    while True:
        print("[DEBUG] Fetching Level 1 semantics...")
        level_1_data = get_level_1_semantics()

        if level_1_data:
            for row in level_1_data:
                print(f"[DEBUG] Processing row ID: {row['id']}")
                combined, result, source_equations = generate_level_2_semantics(row)
                if combined and result:
                    save_level_2_semantics(combined, result, source_equations, row['id'])
                else:
                    print(f"[DEBUG] Not enough data for Level 2 semantics from row ID {row['id']}.")
        else:
            print("[DEBUG] No Level 1 semantics found.")

        print("[DEBUG] Waiting for the next cycle...")
        time.sleep(0)  # Run every hour

if __name__ == "__main__":
    main()
