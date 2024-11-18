import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import QThread
import subprocess
import os
import signal
import init_sql_tables_Default

class WorkerThread(QThread):
    def __init__(self, script):
        super().__init__()
        self.script = script
        self.process = None

    def run(self):
        self.process = subprocess.Popen(['python', self.script])
        self.process.wait()  # Waits for the process to complete

    def stop(self):
        if self.process:
            os.kill(self.process.pid, signal.SIGTERM)
            self.process = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OAI7 Controller")
        self.worker_thread = WorkerThread("first_actions.py")

        self.initUI()

    def initUI(self):
        # Buttons
        start_button = QPushButton("Start")
        stop_button = QPushButton("Stop")

        start_button.clicked.connect(self.start_worker)
        stop_button.clicked.connect(self.stop_worker)

        # Chatbox and input
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)  # Chat display is read-only

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type a message...")
        send_button = QPushButton("Send")

        send_button.clicked.connect(self.send_message)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(start_button)
        button_layout.addWidget(stop_button)

        chat_input_layout = QHBoxLayout()
        chat_input_layout.addWidget(self.input_line)
        chat_input_layout.addWidget(send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addLayout(chat_input_layout)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_worker(self):
        if not self.worker_thread.isRunning():
            self.worker_thread.start()

    def stop_worker(self):
        if self.worker_thread.isRunning():
            self.worker_thread.stop()

    def send_message(self):
        message = self.input_line.text()
        if message.strip():  # Only send non-empty messages
            self.chat_display.append(f"User: {message}")
            self.input_line.clear()

            # Send input to respond.py and capture the response
            response = self.get_response_from_script(message)
            self.chat_display.append(f"OAI7: {response}")

    def get_response_from_script(self, message):
        """Send the user message to respond.py and get the response."""
        try:
            result = subprocess.run(
                ['python', 'respond.py', message],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()  # Return the response from respond.py
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"
def create_schema_and_table():
    init_sql_tables_Default.init_sql_server()

if __name__ == "__main__":
    create_schema_and_table()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
