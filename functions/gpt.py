import time

import openai
import time
Debug = False
import openai
import re
import sql_executor


def gpt_request_semantic(word):
    """
    Sends a request to ChatGPT to generate up to 10 semantic equations for the given word.
    Parses the response and inserts the results into the semantics table.

    Args:
        word (str): The word to generate semantic equations for.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        # System message to guide the response
        system_message = (
            "You are a helpful assistant. Generate up to 10 semantic equations, examples: king + queen = monarch | do not give 1 word response they must be equations "
            "for the given word. Each equation should be denoted as follows: "
            "***Equation_1*** equation ***Equation_2*** equation ... ***Equation_10*** equation. "
            "NEVER PROVIDE EXPLANATIONS above or below the requested information."
        )

        # Prompt the model with the target word
        prompt = f"Generate semantic equations for the word: '{word}'."

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Adjust model as needed
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract response content
        content = response.choices[0].message.content.strip()

        # Parse the response for equations
        equations = {}
        for i in range(1, 11):
            match = re.search(fr"\*\*\*Equation_{i}\*\*\* (.*?)(?=(\*\*\*Equation_\d+\*\*\*)|$)", content, re.DOTALL)
            if match:
                equations[f"chatgpt_response_{i}"] = match.group(1).strip()

        # Prepare insertion query
        if equations:
            columns = ', '.join(equations.keys())

            # Preprocess the values to avoid backslashes in the f-string
            escaped_values = [value.replace("'", "''") for value in equations.values()]
            values = ', '.join([f"'{val}'" for val in escaped_values])

            # Construct the SQL query
            insert_query = (
                "INSERT INTO OA7.level_1_semantics (original_word, " + columns + ") "
                "VALUES ('" + word.replace("'", "''") + "', " + values + ");"
            )

            # Execute the query
            sql_executor.execute_sql(insert_query)
            return "New semantic equations generated and inserted."

        return "No valid semantic equations generated."

    except openai.error.OpenAIError as e:
        # Catch errors related to OpenAI API
        return f"Error in OpenAI API request: {e}"

    except sql_executor.SqlExecutionError as e:
        # Catch specific SQL execution errors if your Sql_executor has custom error handling
        return f"SQL Execution Error: {e}"

    except Exception as e:
        # General exception handler
        return f"An unexpected error occurred: {e}"


def gpt_request_def(word):
    """
    Requests a concise definition for the given word from GPT, with no additional explanation.

    Args:
        word (str): The word to define.

    Returns:
        str: The definition provided by GPT.
    """
    client = openai.OpenAI()
    system_message = "You are an assistant providing concise definitions. Provide only the definition for each word, with no additional explanation."
    full_prompt = f"Define the word '{word}'."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ]
        )

        definition = response.choices[0].message.content.strip()
        return definition

    except Exception as e:
        print(f"Error fetching definition for '{word}': {e}")
        return None
def second_level_gpt_semantics(combined_strings):
    # Create prompt for level 2 semantics
    prompt_modifier = "Use these strings of semantics and see if there are any concepts that could be created by combining them. If you can create a higher-level semantic, output it without explaining."
    full_prompt = f"{prompt_modifier} {combined_strings}"

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate a higher-level semantic concept. using the prompt only, do not create random concepts that are not related to the prompt"},
                {"role": "user", "content": full_prompt}
            ]
        )
        # Extract the output from the response
        level_2_semantic = response.choices[0].message.content.strip()
        return level_2_semantic

    except openai.error.OpenAIError as e:
        print(f"Error generating level 2 semantic: {e}")
        return None


def pos_gpt_request(word):
    # Initialize OpenAI client
    client = openai.OpenAI()

    # Prompt for part of speech determination
    system_message = (
        "You are a helpful assistant providing part of speech information. "
        "Provide only the part of speech (e.g., noun, verb, adjective) for each word, without any additional explanation."
    )
    full_prompt = f"Identify the part of speech for the word '{word}'."

    try:
        # Send the request to OpenAI's GPT model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ]
        )
        # Extract and return the response
        part_of_speech = response.choices[0].message.content.strip()
        return part_of_speech

    except openai.error.OpenAIError as e:
        print(f"Error in pos_gpt_request for '{word}': {e}")
        return None
def isrelated(word1, word2):
    """Checks if two words are related."""
    client = openai.OpenAI()
    system_message = (
        "You are a helpful assistant. Determine if the words are related. its okay if they are not related you can respond with false, you don't have to always have a connection"
        " Respond with 'true' or 'false'."
    )
    full_prompt = f"Are the words '{word1}' and '{word2}' related?"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ]
        )
        result = response.choices[0].message.content.strip().lower()
        return result == "true"

    except Exception as e:
        print(f"Error checking relation between '{word1}' and '{word2}': {e}")
        return False


def howrelated(word1, word2):
    """Gets the concept and definition of the relationship between two words."""
    client = openai.OpenAI()
    system_message = (
        "You are a helpful assistant. Provide a concept that describes the relationship "
        "respond with 1 word for the concept"
    )
    full_prompt = f"What is the concept that describes the relationship between '{word1}' and '{word2}'?"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ]
        )
        concept = response.choices[0].message.content.strip()
        definition = gpt_request_def(concept)  # Assuming you want to define the concept here
        return concept, definition

    except Exception as e:
        print(f"Error getting relationship for '{word1}' and '{word2}': {e}")
        return None, None
import openai

import openai

import openai

def fetch_def_and_pos(word):
    """
    Fetches the definition and part of speech (POS) of a given word from GPT using chat completions.

    Args:
        word (str): The word to define and get POS.

    Returns:
        tuple: A tuple containing the definition and POS of the word, or (None, None) if there was an error.
    """
    # Initialize OpenAI client
    client = openai.OpenAI()

    # System message to instruct GPT to provide both definition and POS
    system_message = (
        "You are an assistant providing concise definitions and part of speech (POS) for words. "
        "Provide the requested definition and POS for each word, with no additional explanation or content above or below the requested information."
    )

    # The prompt asking GPT to define the word and provide its part of speech in the required format
    full_prompt = f"Provide the definition and part of speech (POS) for the word '{word}'. Return the response in the following format: ***Def*** [Definition] ***POS*** [POS]"

    try:
        # Request response from GPT using chat completions
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Replace this with your desired model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ]
        )

        # Extract the response content
        response_content = response.choices[0].message.content.strip()

        # Print the raw GPT response for debugging
        print(f"Raw GPT Response: {response_content}")

        # Ensure response is in the expected format
        if '***Def***' in response_content and '***POS***' in response_content:
            # Split the response into parts
            definition_part = response_content.split('***Def***')[1].split('***POS***')[0].strip()
            pos_part = response_content.split('***POS***')[1].strip()

            # Clean the definition and POS
            definition = definition_part.strip("[]").strip()
            pos = pos_part.strip("[]").strip()

            # Ensure POS is 1 or 2 words max
            if len(pos.split()) > 2:
                pos = ' '.join(pos.split()[:2])

            return definition, pos
        else:
            print(f"Error: Response format incorrect for word '{word}'. GPT response: {response_content}")
            return None, None

    except Exception as e:
        print(f"Error fetching definition and POS for '{word}': {e}")
        return None, None

