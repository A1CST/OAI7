from pynput import mouse
from threading import Thread, Event
import time

class MouseTracker:
    def __init__(self):
        self.events = []
        self.listener = None
        self.stop_event = Event()

    def on_move(self, x, y):
        event = {"type": "move", "position": (x, y)}
        self.events.append(event)
        print(f"Mouse moved to {x}, {y}")

    def on_click(self, x, y, button, pressed):
        action = "pressed" if pressed else "released"
        event = {"type": "click", "position": (x, y), "button": button.name, "action": action}
        self.events.append(event)
        print(f"Mouse {button.name} {action} at {x}, {y}")

    def on_scroll(self, x, y, dx, dy):
        event = {"type": "scroll", "position": (x, y), "scroll": (dx, dy)}
        self.events.append(event)
        print(f"Mouse scrolled at {x}, {y} with delta {dx}, {dy}")

    def start_listener(self):
        with mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        ) as listener:
            self.listener = listener
            self.stop_event.wait()

    def start(self):
        Thread(target=self.start_listener, daemon=True).start()

    def stop(self):
        self.stop_event.set()
        if self.listener:
            self.listener.stop()

    def get_events(self):
        current_events = self.events[:]
        self.events.clear()  # Clear events after returning
        return current_events

def main():
    """Return a snapshot of mouse events captured in a short period."""
    tracker = MouseTracker()
    tracker.start()

    # Collect mouse events for a brief duration
    time.sleep(1)  # Adjust to capture events over a suitable duration
    events = tracker.get_events()
    tracker.stop()

    # Filter and structure the data as needed for the database
    filtered_events = {
        "mouse_position": events[-1]["position"] if events else None,
        "mouse_button": events[-1]["button"] if any(e["type"] == "click" for e in events) else None,
        "mouse_action": events[-1]["action"] if any(e["type"] == "click" for e in events) else None,
        "mouse_scroll": events[-1]["scroll"] if any(e["type"] == "scroll" for e in events) else None
    }

    return filtered_events

if __name__ == "__main__":
    for mouse_events in monitor_system():
        print(f"Returned mouse events: {mouse_events}")
