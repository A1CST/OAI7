"MUST RUN, its on loop every 1 minute"

import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
from schema_expand_NT import create_table  # Assuming this function exists in schema_expand_NT.py
import json
import time
from datetime import datetime

def get_all_tables(schema_name):
    """Retrieve all table names in the given schema."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SHOW TABLES FROM {schema_name}")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"Error fetching tables: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def calculate_averages_and_ranges(table_name):
    """Calculate averages and ranges for numeric and boolean columns in a table."""
    results = []
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get column names and types
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

        numeric_columns = [col['Field'] for col in columns if col['Type'].startswith(('int', 'float', 'double'))]
        boolean_columns = [col['Field'] for col in columns if col['Type'].startswith('tinyint(1)')]

        # Calculate averages and ranges for numeric columns
        for column in numeric_columns:
            cursor.execute(f"SELECT AVG({column}) as avg_value, STDDEV({column}) as std_dev FROM {table_name}")
            result = cursor.fetchone()
            avg = float(result['avg_value']) if result['avg_value'] is not None else None
            std_dev = float(result['std_dev']) if result['std_dev'] is not None else 0
            range_min = avg - (2 * std_dev) if avg is not None else None
            range_max = avg + (2 * std_dev) if avg is not None else None
            results.append({"column": column, "average": avg, "range_min": range_min, "range_max": range_max})

        # Calculate averages for boolean columns
        for column in boolean_columns:
            cursor.execute(f"SELECT AVG({column}) as avg_value FROM {table_name}")
            avg = float(result['avg_value']) if result['avg_value'] is not None else 0
            results.append({"column": column, "average": avg, "range_min": None, "range_max": None})

    except Error as e:
        print(f"Error processing table {table_name}: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return results

def ensure_averages_table():
    """Ensure the Averages table exists by passing required details to schema_expand_NT."""
    table_name = "OA7.Averages"
    columns = {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "column_name": "VARCHAR(255) NOT NULL",
        "average": "FLOAT",
        "range_min": "FLOAT",
        "range_max": "FLOAT",
        "timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    create_table(table_name, columns)  # Pass to schema_expand_NT to ensure table creation

def save_averages_to_db(averages):
    """Save averages to the Averages table."""
    query = """
    INSERT INTO OA7.Averages (column_name, average, range_min, range_max, timestamp)
    VALUES (%s, %s, %s, %s, %s)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        for avg in averages:
            values = (
                avg["column"], avg["average"], avg["range_min"], avg["range_max"], datetime.now()
            )
            cursor.execute(query, values)
        connection.commit()
        print(f"Averages saved to database.")
    except Error as e:
        print(f"Error saving averages to database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    schema_name = "OA7"
    ensure_averages_table()  # Ensure the table exists
    while True:
        tables = get_all_tables(schema_name)
        for table in tables:
            print(f"Processing table: {table}")
            averages = calculate_averages_and_ranges(f"{schema_name}.{table}")
            save_averages_to_db(averages)
        time.sleep(30)  # Wait for 30 seconds before the next run

if __name__ == "__main__":
    main()
