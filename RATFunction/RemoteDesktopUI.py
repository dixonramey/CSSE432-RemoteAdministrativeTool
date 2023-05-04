import io

from PIL import Image
from PIL.ImageQt import ImageQt
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
        self.button = QPushButton('Enable Remote Desktop', self)
        self.button.clicked.connect(self.enable_remote_desktop)

        # Create label and set pixmap
        self.label = QLabel()
        self.label.setFixedSize(1280, 720)
        self.label.setScaledContents(True)
        # self.label.setAspectRatioMode(Qt.KeepAspectRatio)
        self.pixmap = QPixmap()

        # Create layout and add label to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # Set the layout for the widget
        self.setLayout(layout)

    def received_image_callback(self, image_bytes):
        QPixmap.loadFromData(self.pixmap, image_bytes, format='JPEG')
        self.label.setPixmap(self.pixmap)

    def enable_remote_desktop(self):
        self.remote_desktop_function.send_set_state(True)
