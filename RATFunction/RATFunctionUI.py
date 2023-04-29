from PyQt5.QtWidgets import QWidget


class RATFunctionUI(QWidget):
    def __init__(self, function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function = function
