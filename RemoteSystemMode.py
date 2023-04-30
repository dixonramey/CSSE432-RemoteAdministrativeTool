import hashlib
import struct
import threading

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from RATConnection import RATServer
from RATFunction.RATFunction import Side
from RATFunction.RATFunctionRegistry import RATFunctionRegistry


class RemoteSystemMode(QWidget):
    def __init__(self, function_classes, password):
        super().__init__()
        self.server = RATServer()
        self.registry = RATFunctionRegistry()
        self.password = password
        self.admin_authorized = False

        for function_class in function_classes:
            self.registry.add_function(function_class(Side.REMOTE_SIDE, self.server.packet_queue))

        hash_object = hashlib.sha256()
        hash_object.update(self.password.encode())
        self.password_hash = hash_object.digest()

        self.setup_gui()

        threading.Thread(target=self._start_server, daemon=True).start()

    def setup_gui(self):
        self.layout = QVBoxLayout()
        # add a label to the layout
        self.label = QLabel("Running as Remote System")
        self.layout.addWidget(self.label)
        # set the layout for the dialog
        self.setLayout(self.layout)
        # set the window title and size
        self.setWindowTitle("RAT")
        self.setFixedSize(300, 150)

    def _start_server(self, port=8888):
        self.server.packet_callback = self.handle_packet
        self.server.client_disconnected_callback = self.client_disconnected
        self.server.listen(port)

    def client_disconnected(self):
        self.admin_authorized = False

    def handle_packet(self, data):
        packet_id, b = struct.unpack("I 2044s", data)

        if self.admin_authorized:
            self.registry.route_packet(data)
        elif packet_id == 0:
            password_attempt = b[:32]
            if self.try_authorize(password_attempt):
                self.admin_authorized = True
            else:
                print("Incorrect password, closing connection")
                self.server.get_sock().close()

    def try_authorize(self, password_attempt_hash) -> bool:
        return self.password_hash == password_attempt_hash
