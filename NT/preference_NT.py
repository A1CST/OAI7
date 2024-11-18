import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import time
from collections import Counter

def get_preference_for_column(column_name, exclude_na=False):
    """Fetch the most frequently occurring value for a given column, with optional exclusion of 'N/A' and empty values."""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = f"SELECT `{column_name}` FROM OA7.sensory_input WHERE `{column_name}` IS NOT NULL"
        cursor.execute(query)
        values = [row[0] for row in cursor.fetchall()]

        if exclude_na:
            values = [value for value in values if value not in ("N/A", "", None)]

        if values:
            most_common_value = Counter(values).most_common(1)[0][0]
            return most_common_value
        return None
    except Error as e:
        print(f"Error fetching preference for column '{column_name}': {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_preference_to_db(column_name, preferred_value):
    """Save or update the preferred value for a column in the preferences table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO OA7.preferences (column_name, preferred_value)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE 
            preferred_value = VALUES(preferred_value),
            timestamp = CURRENT_TIMESTAMP;
        """, (column_name, preferred_value))

        connection.commit()
        print(f"Preference for '{column_name}' saved: {preferred_value}")
    except Error as e:
        print(f"Error saving preference for '{column_name}': {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    columns = [
        "cpu_usage", "ram_usage_percent", "ram_used_mb", "ram_total_mb",
        "hdd_usage_percent", "hdd_used_gb", "hdd_total_gb",
        "gpu_utilization_percent", "gpu_memory_used_mb", "gpu_memory_total_mb",
        "key_pressed", "mouse_position", "mouse_button", "mouse_action", "mouse_scroll"
    ]

    # Columns where 'N/A' and empty values should be excluded
    exclude_na_columns = {"key_pressed", "mouse_position", "mouse_button", "mouse_action", "mouse_scroll"}

    while True:
        print("Calculating preferences...")
        for column in columns:
            exclude_na = column in exclude_na_columns
            preference = get_preference_for_column(column, exclude_na=exclude_na)
            if preference is not None:
                save_preference_to_db(column, preference)
            else:
                print(f"No valid data available for column: {column}")

        print("Waiting for 30 seconds before the next update...")
        time.sleep(30)

if __name__ == "__main__":
    main()
