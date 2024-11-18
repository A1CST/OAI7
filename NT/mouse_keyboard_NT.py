"MUST RUN, its on loop every 1 second"
import random
import time
from datetime import datetime
import pyautogui  # Library to get screen resolution
from sql_executor import execute_sql_with_args  # Assuming this function is already available

def get_screen_resolution():
    """Retrieve the screen resolution."""
    screen_width, screen_height = pyautogui.size()
    return screen_width, screen_height

def simulate_mouse_movement(screen_width, screen_height):
    """Simulate mouse movement with random coordinates within screen bounds."""
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    return {"input_type": "mouse_move", "mouse_x": x, "mouse_y": y}

def simulate_mouse_click(screen_width, screen_height):
    """Simulate a mouse click at a random position within screen bounds."""
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    button = random.choice(["left", "right", "middle"])
    return {"input_type": "mouse_click", "mouse_x": x, "mouse_y": y, "mouse_button": button}

def simulate_mouse_scroll(screen_width, screen_height):
    """Simulate a mouse scroll at a random position within screen bounds."""
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    scroll_amount = random.choice(["up", "down"])
    return {"input_type": "mouse_scroll", "mouse_x": x, "mouse_y": y, "scroll_direction": scroll_amount}

def simulate_key_press():
    """Simulate a random key press."""
    key = random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
    return {"input_type": "key_press", "key_pressed": key}

def save_to_sql(action):
    """Save simulated touch actions to the SQL database."""
    query = """
    INSERT INTO OA7.input_log (input_type, mouse_x, mouse_y, mouse_button, scroll_direction, key_pressed, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        action.get("input_type"),
        action.get("mouse_x"),
        action.get("mouse_y"),
        action.get("mouse_button"),
        action.get("scroll_direction"),
        action.get("key_pressed"),
        datetime.now(),
    )
    execute_sql_with_args(query, values)
    print(f"Action saved to SQL: {action}")

def main():
    screen_width, screen_height = get_screen_resolution()
    print(f"Screen resolution detected: {screen_width}x{screen_height}")

    while True:
        action_type = random.choice(["mouse_move", "mouse_click", "mouse_scroll", "key_press"])
        if action_type == "mouse_move":
            action = simulate_mouse_movement(screen_width, screen_height)
        elif action_type == "mouse_click":
            action = simulate_mouse_click(screen_width, screen_height)
        elif action_type == "mouse_scroll":
            action = simulate_mouse_scroll(screen_width, screen_height)
        elif action_type == "key_press":
            action = simulate_key_press()

        save_to_sql(action)
        time.sleep(1)  # Simulate an action every second

if __name__ == "__main__":
    main()
