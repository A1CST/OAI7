"Called as needed"

import mysql.connector
from mysql.connector import Error
from sql_executor import execute_sql  # Assuming you have sql_executor functions ready


def create_table(table_name, columns, foreign_keys=None):
    """
    Dynamically creates a table in the database.

    :param table_name: Name of the table to be created
    :param columns: A dictionary where keys are column names and values are data types
    :param foreign_keys: A list of foreign key constraints, each as a dictionary with:
                         - 'column': The column in the new table
                         - 'reference_table': The table being referenced
                         - 'reference_column': The column in the referenced table
    """
    column_definitions = []
    for col_name, col_type in columns.items():
        column_definitions.append(f"{col_name} {col_type}")

    # Add foreign key constraints if provided
    if foreign_keys:
        for fk in foreign_keys:
            column_definitions.append(
                f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['reference_table']}({fk['reference_column']}) ON DELETE CASCADE"
            )

    column_definitions_str = ", ".join(column_definitions)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions_str});"

    try:
        execute_sql(query)
        print(f"Table '{table_name}' created successfully.")
    except Error as e:
        print(f"Error creating table '{table_name}': {e}")


# Example usage
if __name__ == "__main__":
    table_name = "example_table"
    columns = {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "name": "VARCHAR(255) NOT NULL",
        "age": "INT",
        "address_id": "INT"
    }
    foreign_keys = [
        {"column": "address_id", "reference_table": "addresses", "reference_column": "id"}
    ]
    create_table(table_name, columns, foreign_keys)
