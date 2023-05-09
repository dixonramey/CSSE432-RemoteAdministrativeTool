from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton

from RATFunction.RATFunctionUI import RATFunctionUI
from RATFunction.RemoteDesktop import RemoteDesktop


class RemoteDesktopUI(RATFunctionUI):
    def __init__(self, function: RemoteDesktop, *args, **kwargs):
        super().__init__(function, *args, **kwargs)
        self.remote_desktop_function = function
        self.remote_desktop_function.received_image_callback = self.received_image_callback

        self.setWindowTitle('Remote Desktop')

        # Create label and set pixmap
        self.label = RemoteDesktopView()
        self.label.setFixedSize(1280, 720)
        self.label.setScaledContents(True)
        self.label.mouse_event_callback = self.mouse_event_callback
        self.pixmap = QPixmap()

        # Create layout and add label to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # Set the layout for the widget
        self.setLayout(layout)

    def show(self):
        super().show()
        self.remote_desktop_function.send_set_state(True)

    def closeEvent(self, event):
        self.remote_desktop_function.send_set_state(False)
        event.accept()

    def mouse_event_callback(self, event_id, x, y):
        x, y = self.translate_coords(x, y)

        if event_id == 1:
            self.remote_desktop_function.send_left_click(x, y)
        elif event_id == 2:
            self.remote_desktop_function.send_right_click(x, y)

    def translate_coords(self, x, y):
        return int((x / self.label.size().width()) * 1920), int((y / self.label.size().height()) * 1080)

    def received_image_callback(self, image_bytes):
        QPixmap.loadFromData(self.pixmap, image_bytes, format='JPEG')
        self.label.setPixmap(self.pixmap)


class RemoteDesktopView(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mouse_event_callback = lambda event_id, x, y: ()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_event_callback(1, event.x(), event.y())
        elif event.button() == Qt.RightButton:
            self.mouse_event_callback(2, event.x(), event.y())
