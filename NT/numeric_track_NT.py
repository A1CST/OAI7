import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import json
import time


def get_all_tables():
    """Fetch all table names from the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES FROM OA7")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"Error fetching tables: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def count_numeric_occurrences(table, column):
    """Count occurrences of numeric values in a specific column of a table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {column} FROM OA7.{table}")
        rows = cursor.fetchall()
        occurrences = {}
        for row in rows:
            value = row[0]
            if isinstance(value, (int, float)):
                value_str = str(value)
                occurrences[value_str] = occurrences.get(value_str, 0) + 1
        return occurrences
    except Error as e:
        print(f"Error counting numeric occurrences for '{column}' in '{table}': {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def aggregate_numeric_preferences():
    """Aggregate numeric preferences across all tables and columns."""
    tables = get_all_tables()
    aggregated_preferences = {}
    for table in tables:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(f"DESCRIBE OA7.{table}")
            columns = cursor.fetchall()
            numeric_columns = [col[0] for col in columns if col[1].startswith(('int', 'float', 'double', 'decimal'))]

            for column in numeric_columns:
                occurrences = count_numeric_occurrences(table, column)
                for value, count in occurrences.items():
                    if float(value) == 1.0 or count < 5:
                        continue
                    if value in aggregated_preferences:
                        aggregated_preferences[value] += count
                    else:
                        aggregated_preferences[value] = count

        except Error as e:
            print(f"Error processing table {table}: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return aggregated_preferences


def save_numeric_preferences(preferences):
    """Save the top 100 numeric preferences to the numeric_preferences table."""
    sorted_preferences = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
    top_100 = sorted_preferences[:100]

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM OA7.numeric_preferences")  # Clear previous entries
        for value, count in top_100:
            cursor.execute("""
            INSERT INTO OA7.numeric_preferences (value, occurrence, timestamp)
            VALUES (%s, %s, NOW())
            """, (value, count))
        connection.commit()
        print(f"Saved top {len(top_100)} numeric preferences to the database.")
    except Error as e:
        print(f"Error saving numeric preferences: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    while True:
        print("Scanning all tables for numeric preferences...")
        preferences = aggregate_numeric_preferences()
        if preferences:
            save_numeric_preferences(preferences)
        else:
            print("No numeric preferences found.")
        print("Waiting for 16 hours before the next scan...")
        time.sleep(57600)  # 16 hours


if __name__ == "__main__":
    main()
