import os
import time
import importlib.util
from sql_executor import execute_sql_with_args


def load_and_run_script(script_path):
    """
    Dynamically loads and runs a Python script, returning its result.
    """
    try:
        spec = importlib.util.spec_from_file_location("module.name", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"Running script: {script_path}")
        if hasattr(module, 'main'):
            result = module.main()  # Assumes each script has a `main()` function
            if result:
                print(f"Script {script_path} returned: {result}")
                return result
            else:
                print(f"Script {script_path} returned no data.")
                return {}
        else:
            print(f"Script {script_path} has no 'main()' function.")
            return {}
    except Exception as e:
        print(f"Error running {script_path}: {e}")
        return {}


def gather_data():
    """
    Runs all scripts in the /senses directory and gathers their data.
    """
    senses_dir = './senses'
    scripts = [os.path.join(senses_dir, file) for file in os.listdir(senses_dir) if file.endswith('.py')]

    collected_data = {}
    for script in scripts:
        result = load_and_run_script(script)
        collected_data.update(result)

    return collected_data


def validate_data(data):
    """
    Ensures all fields in the data are populated.
    """
    required_fields = [
        "cpu_usage", "ram_usage_percent", "ram_used_mb", "ram_total_mb",
        "hdd_usage_percent", "hdd_used_gb", "hdd_total_gb",
        "gpu_utilization_percent", "gpu_memory_used_mb", "gpu_memory_total_mb",
        "key_pressed", "mouse_position", "mouse_button", "mouse_action", "mouse_scroll"
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            data[field] = "N/A"  # Placeholder for missing data

    # Convert list fields to strings
    if isinstance(data.get("key_pressed"), list):
        data["key_pressed"] = ", ".join(data["key_pressed"])

    # Convert tuple fields to strings
    if isinstance(data.get("mouse_position"), tuple):
        data["mouse_position"] = str(data["mouse_position"])

    return data


def save_to_database(data):
    """
    Saves the validated data to the sensory_input table.
    """
    sql = """
    INSERT INTO OA7.sensory_input (
        cpu_usage, ram_usage_percent, ram_used_mb, ram_total_mb, 
        hdd_usage_percent, hdd_used_gb, hdd_total_gb, 
        gpu_utilization_percent, gpu_memory_used_mb, gpu_memory_total_mb, 
        key_pressed, mouse_position, mouse_button, mouse_action, mouse_scroll
    ) VALUES (
        %(cpu_usage)s, %(ram_usage_percent)s, %(ram_used_mb)s, %(ram_total_mb)s, 
        %(hdd_usage_percent)s, %(hdd_used_gb)s, %(hdd_total_gb)s, 
        %(gpu_utilization_percent)s, %(gpu_memory_used_mb)s, %(gpu_memory_total_mb)s, 
        %(key_pressed)s, %(mouse_position)s, %(mouse_button)s, %(mouse_action)s, %(mouse_scroll)s
    );
    """
    try:
        execute_sql_with_args(sql, data)
        print("Data successfully saved to database.")
    except Exception as e:
        print(f"Error saving data to database: {e}")


def main():
    print("Initializing data collection from /senses...")

    try:
        while True:
            collected_data = gather_data()
            validated_data = validate_data(collected_data)
            save_to_database(validated_data)
            time.sleep(5)  # Pause for 5 seconds between uploads
    except KeyboardInterrupt:
        print("Stopping data collection...")


if __name__ == "__main__":
    main()
