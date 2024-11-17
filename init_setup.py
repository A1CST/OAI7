import os
import mysql.connector
from mysql.connector import errorcode


def create_user_and_database(ip_address, root_user):
    try:
        # Connect to MySQL server as root
        connection = mysql.connector.connect(
            host=ip_address,
            user=root_user,
            password=""  # Root password is blank
        )
        cursor = connection.cursor()

        # Create a new user
        new_user = 'oai_user'
        new_password = ''  # Blank password for the new user
        try:
            cursor.execute(f"CREATE USER '{new_user}'@'%' IDENTIFIED BY '{new_password}';")
            print(f"User '{new_user}' created successfully.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_CANNOT_USER:
                print(f"User '{new_user}' already exists.")
            else:
                raise

        # Grant all privileges to the new user
        cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{new_user}'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")
        print(f"Privileges granted to user '{new_user}'.")

        # Write connection details to init_sql.py
        write_connection_file(ip_address, new_user, new_password)

        # Ensure sql_executor.py is created before using it
        create_sql_executor()

        # Now create schema and table
        create_schema_and_table()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Please check your IP or root credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")


def write_connection_file(ip_address, user, password):
    content = f"""
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='{ip_address}',
        user='{user}',
        password='{password}',
        database=None  # Specify the database if needed
    )
"""
    with open("init_sql.py", "w") as f:
        f.write(content.strip())
    print("Connection details saved to init_sql.py.")


def create_sql_executor():
    content = """
import mysql.connector
from mysql.connector import Error
from init_sql import get_connection

def execute_sql(statement):
    \"\"\"
    Executes a given SQL statement without arguments.
    :param statement: SQL query to execute
    \"\"\"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        print(f"Executing SQL: {statement}")
        cursor.execute(statement)
        connection.commit()
        print("Execution successful.")
    except Error as e:
        print(f"Error executing SQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")

def execute_sql_with_args(statement, args):
    \"\"\"
    Executes a given SQL statement with arguments.
    :param statement: SQL query to execute
    :param args: Tuple of arguments for the SQL query
    \"\"\"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        print(f"Executing SQL: {statement} with arguments: {args}")
        cursor.execute(statement, args)
        connection.commit()
        print("Execution successful.")
    except Error as e:
        print(f"Error executing SQL with arguments: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")
"""
    with open("sql_executor.py", "w") as f:
        f.write(content.strip())
    print("sql_executor.py created successfully.")


def create_schema_and_table():
    from sql_executor import execute_sql

    schema_statement = "CREATE SCHEMA IF NOT EXISTS OA7;"
    table_statement = """
    CREATE TABLE IF NOT EXISTS OA7.sensory_input (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cpu_usage FLOAT,
        ram_usage_percent FLOAT,
        ram_used_mb FLOAT,
        ram_total_mb FLOAT,
        hdd_usage_percent FLOAT,
        hdd_used_gb FLOAT,
        hdd_total_gb FLOAT,
        gpu_utilization_percent FLOAT,
        gpu_memory_used_mb FLOAT,
        gpu_memory_total_mb FLOAT,
        key_pressed TEXT,
        mouse_position TEXT,
        mouse_button TEXT,
        mouse_action TEXT,
        mouse_scroll TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_sql(schema_statement)
    print("Schema OA7 created or verified.")

    execute_sql(table_statement)
    print("Table sensory_input created or verified.")


def main():
    print("Welcome to OAI MySQL Setup")
    ip_address = input("Enter your MySQL server IP address: ").strip()
    root_user = input("Enter your MySQL root username (default: root): ").strip() or "root"

    create_user_and_database(ip_address, root_user)


if __name__ == "__main__":
    main()
