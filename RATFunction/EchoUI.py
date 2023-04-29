import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout

from RATFunction.Echo import Echo
from RATFunction.RATFunctionUI import RATFunctionUI


class EchoUI(RATFunctionUI):
    def __init__(self, function: Echo):
        super().__init__(function)
        self.echo_function = function
        self.echo_function.received_echo_callback = self.received_echo_callback

        # Create a QLineEdit widget for text input
        self.text_input = QLineEdit(self)

        # Create a QPushButton widget for button press
        self.button = QPushButton('Send Echo', self)
        self.button.clicked.connect(self.send_echo)

        # Create a vertical layout and add the widgets to it
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_input)
        layout.addWidget(self.button)

        self.setMinimumSize(500, 100)

    def send_echo(self):
        text = self.text_input.text()
        self.echo_function.send_echo(text)

    def received_echo_callback(self, text):
        self.setWindowTitle(f"Received Echo: {text}")

