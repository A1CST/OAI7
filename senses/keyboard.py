from pynput import keyboard
from threading import Thread, Event
import time


class KeystrokeTracker:
    def __init__(self):
        self.keystrokes = []
        self.listener = None
        self.stop_event = Event()

    def on_press(self, key):
        try:
            key_value = key.char if key.char else str(key)
        except AttributeError:
            key_value = str(key)

        self.keystrokes.append(key_value)
        print(f"Key pressed: {key_value}")

    def start_listener(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            self.listener = listener
            self.stop_event.wait()

    def start(self):
        Thread(target=self.start_listener, daemon=True).start()

    def stop(self):
        self.stop_event.set()
        if self.listener:
            self.listener.stop()

    def get_keystrokes(self):
        current_keystrokes = self.keystrokes[:]
        self.keystrokes.clear()  # Reset after returning to avoid duplication
        return current_keystrokes


def main():
    """Return a snapshot of keystrokes captured in a short period."""
    tracker = KeystrokeTracker()
    tracker.start()

    # Collect keystrokes for a short duration
    time.sleep(1)  # Adjust as needed for the sampling duration
    keystrokes = tracker.get_keystrokes()
    tracker.stop()

    return {"key_pressed": keystrokes}


if __name__ == "__main__":
    for keystrokes in track_keystrokes():
        print(f"Returned keystrokes: {keystrokes}")
