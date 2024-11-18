import mysql.connector
from mysql.connector import errorcode
from init_sql import get_connection
from mysql.connector import Error

def create_base_tables():
    """Function to create base tables. Add cursor.execute statements for each table."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.user_txt_input (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_input TEXT NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
                """)
        cursor.execute("""CREATE TABLE IF NOT EXISTS OA7.sensory_input (
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
    """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OA7.input_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_type ENUM('mouse_move', 'mouse_click', 'mouse_scroll', 'key_press') NOT NULL,
            mouse_x INT,  -- X coordinate for mouse actions
            mouse_y INT,  -- Y coordinate for mouse actions
            mouse_button ENUM('left', 'right', 'middle') DEFAULT NULL,  -- Mouse button if applicable
            scroll_direction ENUM('up', 'down') DEFAULT NULL,  -- Scroll direction if applicable
            key_pressed CHAR(1) DEFAULT NULL,  -- Key pressed if applicable
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OA7.word_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(255) NOT NULL UNIQUE,
        definition TEXT,
        occurrence_count INT DEFAULT 0,
        explicit BOOLEAN DEFAULT FALSE,
        part_of_speech VARCHAR(50),
        parent_id INT,  -- Foreign key to user_txt_input table
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES OA7.user_txt_input(id) ON DELETE CASCADE
    );

        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS OA7.level_1_semantics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_word VARCHAR(255),
            original_word_id INT,  -- Foreign key to words_data table
            hierarchy_level INT DEFAULT 1,
            connection_strength FLOAT DEFAULT 1.0,
            parent_id INT DEFAULT NULL,
            chatgpt_response_1 TEXT,
            chatgpt_response_2 TEXT,
            chatgpt_response_3 TEXT,
            chatgpt_response_4 TEXT,
            chatgpt_response_5 TEXT,
            chatgpt_response_6 TEXT,
            chatgpt_response_7 TEXT,
            chatgpt_response_8 TEXT,
            chatgpt_response_9 TEXT,
            chatgpt_response_10 TEXT,
            higher_semantic BOOLEAN DEFAULT 0,
            FOREIGN KEY (original_word_id) REFERENCES OA7.word_data(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES OA7.level_1_semantics(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.grammar_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    template TEXT NOT NULL,
                    occurrences INT DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    conversation_id INT,
                    processed BOOLEAN DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES OA7.conversations(id) ON DELETE CASCADE
                );
                """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.patterns (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    grammar_template_id1 INT NOT NULL,
                    grammar_template_id2 INT NOT NULL,
                    pattern TEXT NOT NULL,
                    occurrence INT DEFAULT 1,
                    processed BOOLEAN DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (grammar_template_id1) REFERENCES OA7.grammar_templates(id) ON DELETE CASCADE,
                    FOREIGN KEY (grammar_template_id2) REFERENCES OA7.grammar_templates(id) ON DELETE CASCADE
                );
                """)
        # Create conversations table
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                OAI_response TEXT,
                gpt_response TEXT,
                processed BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                grammar_process BOOLEAN DEFAULT 0
            );

                """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.preferences (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    column_name VARCHAR(255) NOT NULL,
                    preferred_value TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_preference (column_name)
                );
                """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS OA7.numeric_preferences (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    value VARCHAR(255) NOT NULL,
                    occurrence INT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS OA7.level_2_semantics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            combined_elements TEXT NOT NULL,  -- Combination of Level 1 semantic results
            result TEXT NOT NULL,  -- The generated Level 2 semantic concept
            parent_id TEXT NOT NULL,  -- IDs of parent Level 1 semantics (stored as a delimited string)
            higher_semantic BOOLEAN DEFAULT 0,  -- Indicates if this has contributed to a Level 3 semantic
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Record creation time
        );
            """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OA7.grammar_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pattern TEXT NOT NULL,  -- Stores the pattern using parts of speech
    occurrence_count INT DEFAULT 1,  -- Counts occurrences of the same POS pattern
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES OA7.patterns(id) ON DELETE CASCADE -- Links back to the source pattern
);
""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OA7.level_3_semantics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    combined_elements TEXT NOT NULL,  -- Combination of Level 2 semantic results
    result TEXT NOT NULL,  -- The generated Level 3 semantic concept
    parent_ids TEXT NOT NULL,  -- IDs of parent Level 2 semantics (stored as a delimited string)
    higher_semantic BOOLEAN DEFAULT 0,  -- Indicates if this has contributed to a higher-level semantic
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Record creation time
);
""")

        print("Base tables created successfully.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Please check your credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed.")

def create_schema(schema_name="OA7"):
    """Creates a schema if it doesn't already exist."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        connection.commit()
        print(f"Schema '{schema_name}' created or already exists.")
    except Error as e:
        print(f"Error creating schema '{schema_name}': {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def init_sql_server():
    create_schema()
    create_base_tables()

if __name__ == "__main__":
    create_schema()
    create_base_tables()
