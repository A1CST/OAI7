import mysql.connector
from mysql.connector import Error
from init_sql import get_connection
import time


def get_templates():
    """Fetch all unprocessed templates from the grammar_templates table."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT id, template 
        FROM OA7.grammar_templates
        WHERE processed = 0;
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching templates: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def find_patterns(templates):
    """Identify repeating patterns between IDs in the templates."""
    patterns = {}
    for i, template1 in enumerate(templates):
        ids1 = template1['template'].split()
        for j, template2 in enumerate(templates):
            if i >= j:
                continue  # Avoid comparing a row with itself or re-checking pairs
            ids2 = template2['template'].split()

            # Find common subsequences between the two templates
            for length in range(2, min(len(ids1), len(ids2)) + 1):
                for start in range(len(ids1) - length + 1):
                    subsequence = ids1[start:start + length]
                    if subsequence in [ids2[k:k + length] for k in range(len(ids2) - length + 1)]:
                        pattern = " ".join(subsequence)
                        pattern_key = (pattern, template1['id'], template2['id'])

                        if pattern_key in patterns:
                            patterns[pattern_key]['occurrence'] += 1
                        else:
                            patterns[pattern_key] = {
                                "grammar_template_id1": template1['id'],
                                "grammar_template_id2": template2['id'],
                                "pattern": pattern,
                                "occurrence": 1
                            }
    return list(patterns.values())


def save_patterns_to_table(patterns):
    """Save identified patterns to the patterns table, updating occurrences if patterns already exist."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        processed_templates = set()  # Track processed templates

        for pattern in patterns:
            cursor.execute("""
            SELECT id, occurrence FROM OA7.patterns 
            WHERE grammar_template_id1 = %s AND grammar_template_id2 = %s AND pattern = %s;
            """, (pattern['grammar_template_id1'], pattern['grammar_template_id2'], pattern['pattern']))
            existing = cursor.fetchone()

            if existing:
                new_occurrence = existing[1] + pattern['occurrence']
                cursor.execute("""
                UPDATE OA7.patterns SET occurrence = %s WHERE id = %s;
                """, (new_occurrence, existing[0]))
                print(f"Updated occurrence count for pattern: {pattern['pattern']}")
            else:
                cursor.execute("""
                INSERT INTO OA7.patterns (grammar_template_id1, grammar_template_id2, pattern, occurrence)
                VALUES (%s, %s, %s, %s);
                """, (pattern['grammar_template_id1'], pattern['grammar_template_id2'], pattern['pattern'],
                      pattern['occurrence']))
                print(f"Inserted new pattern: {pattern['pattern']}")

            # Mark templates as processed
            processed_templates.add(pattern['grammar_template_id1'])
            processed_templates.add(pattern['grammar_template_id2'])

        connection.commit()

        # Mark all templates involved in patterns as processed
        for template_id in processed_templates:
            mark_template_as_processed(template_id)
    except Error as e:
        print(f"Error saving patterns to database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def mark_template_as_processed(template_id):
    """Mark a grammar template as processed."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE OA7.grammar_templates 
        SET processed = 1 
        WHERE id = %s;
        """, (template_id,))
        connection.commit()
        print(f"Marked template ID {template_id} as processed.")
    except Error as e:
        print(f"Error marking template as processed: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    while True:
        print("Fetching templates for pattern detection...")
        templates = get_templates()
        if templates:
            print(f"Analyzing {len(templates)} templates for patterns...")
            patterns = find_patterns(templates)
            if patterns:
                save_patterns_to_table(patterns)
            else:
                print("No patterns found.")
        else:
            print("No unprocessed templates to process.")
        print("Waiting for the next cycle...")
        time.sleep(60)  # Run every 60 seconds


if __name__ == "__main__":
    main()
