import mysql.connector
from mysql.connector import Error
from init_sql import get_connection

def execute_sql(statement):
    """
    Executes a given SQL statement without arguments.
    :param statement: SQL query to execute
    """
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
    """
    Executes a given SQL statement with arguments.
    :param statement: SQL query to execute
    :param args: Tuple of arguments for the SQL query
    """
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