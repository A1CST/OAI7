import mysql.connector
from mysql.connector import Error
from init_sql import get_connection

def drop_schema(schema_name="OA7"):
    """Drops the entire schema, including all tables and data."""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name}")
        print(f"Schema '{schema_name}' has been dropped successfully.")

        connection.commit()

    except Error as e:
        print(f"Error dropping schema: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    drop_schema()
