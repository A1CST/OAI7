import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
from functions.gpt import third_level_gpt_semantics  # Import the Level 3 GPT function
import time

BATCH_SIZE = 10  # Limit the number of rows processed in each cycle

def get_level_2_semantics(batch_size=BATCH_SIZE, offset=0):
    """Fetch Level 2 semantics from the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"""
        SELECT id, result, combined_elements
        FROM OA7.level_2_semantics
        WHERE higher_semantic = 0
        LIMIT {batch_size} OFFSET {offset};
        """)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Error fetching Level 2 semantics: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_level_3_semantics(combined, result, parent_ids):
    """Save Level 3 semantics into the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO OA7.level_3_semantics (combined_elements, result, parent_ids)
        VALUES (%s, %s, %s);
        """, (combined, result, parent_ids))
        connection.commit()
        print(f"Saved Level 3 Semantic: {combined} = {result}")
    except Error as e:
        print(f"Error saving Level 3 semantics: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def mark_level_2_as_processed(level_2_ids):
    """Mark Level 2 semantics as processed."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"""
        UPDATE OA7.level_2_semantics 
        SET higher_semantic = 1 
        WHERE id IN ({",".join(map(str, level_2_ids))});
        """)
        connection.commit()
        print(f"Marked Level 2 IDs as processed: {level_2_ids}")
    except Error as e:
        print(f"Error updating Level 2 semantics: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def process_level_2_semantics(level_2_data):
    """Generate Level 3 semantics from Level 2 data."""
    combined_elements = []
    parent_ids = []

    for row in level_2_data:
        combined_elements.append(row['result'])
        parent_ids.append(str(row['id']))

    if len(combined_elements) >= 2:
        combined_str = " + ".join(combined_elements[:4])  # Limit to 4 inputs for a more abstract result
        result = third_level_gpt_semantics(combined_str)
        return combined_str, result, ";".join(parent_ids)

    return None, None, None

def main():
    offset = 0
    while True:
        print("Fetching Level 2 semantics...")
        level_2_data = get_level_2_semantics(offset=offset)

        if level_2_data:
            combined, result, parent_ids = process_level_2_semantics(level_2_data)
            if combined and result:
                save_level_3_semantics(combined, result, parent_ids)
                mark_level_2_as_processed([row['id'] for row in level_2_data])
            else:
                print("Not enough data to generate Level 3 semantics.")
            offset += BATCH_SIZE
        else:
            print("No Level 2 semantics left. Resetting offset.")
            offset = 0

        print("Waiting for the next cycle...")
        time.sleep(3) # Run every hour

if __name__ == "__main__":
    main()
