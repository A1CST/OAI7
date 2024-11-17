import socket
import json
import time
import random

HOST = 'localhost'
PORT = 25565


def generate_mouse_input():
    """Generate random mouse movement and click input."""
    x = random.randint(0, 800)  # Adjust based on VM resolution
    y = random.randint(0, 600)
    click = random.choice([None, {"button": "left"}, {"button": "right"}])

    input_data = {"mouse": {"x": x, "y": y}}

    if click:
        input_data["click"] = click

    return input_data


def generate_keyboard_input():
    """Generate random keyboard input."""
    keys = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    return {"keypress": random.choice(keys)}


def main():
    """Main loop for OAI agent."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            # Decide between mouse or keyboard input
            if random.random() > 0.5:
                input_data = generate_mouse_input()
            else:
                input_data = generate_keyboard_input()

            # Send input to the environment
            s.sendall(json.dumps(input_data).encode('utf-8'))
            print(f"Sent: {input_data}")

            # Wait for next action
            time.sleep(1)  # Adjust for desired input frequency


if __name__ == "__main__":
    main()
