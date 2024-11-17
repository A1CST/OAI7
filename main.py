import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread
import subprocess
import os
import signal

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
        start_button = QPushButton("Start")
        stop_button = QPushButton("Stop")

        start_button.clicked.connect(self.start_worker)
        stop_button.clicked.connect(self.stop_worker)

        layout = QVBoxLayout()
        layout.addWidget(start_button)
        layout.addWidget(stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_worker(self):
        if not self.worker_thread.isRunning():
            self.worker_thread.start()

    def stop_worker(self):
        if self.worker_thread.isRunning():
            self.worker_thread.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
