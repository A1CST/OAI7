import os
import mysql.connector
from mysql.connector import errorcode

import init_sql_tables_Default
from init_sql_tables_Default import create_base_tables  # Import from init_sql_tables_Default

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
    \"\"\"Executes a given SQL statement without arguments.\"\"\"
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
    \"\"\"Executes a given SQL statement with arguments.\"\"\"
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
    init_sql_tables_Default.init_sql_server()


def main():
    print("Welcome to OAI MySQL Setup")
    ip_address = input("Enter your MySQL server IP address: ").strip()
    root_user = input("Enter your MySQL root username (default: root): ").strip() or "root"

    create_user_and_database(ip_address, root_user)


if __name__ == "__main__":
    main()
