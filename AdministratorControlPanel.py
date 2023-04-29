import sys
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton

from RATConnection import RATClient
from RATFunction.EchoUI import EchoUI
from RATFunction.RATFunction import Side
from RATFunction.RATFunctionRegistry import RATFunctionRegistry


class AdminNetworkThread(QThread):
    received_packet = pyqtSignal(bytes)

    def __init__(self, client: RATClient, host, port, parent=None):
        super().__init__(parent)
        self.client = client
        self.host = host
        self.port = port

    def run(self):
        print("running network thread")
        while True:
            try:
                print(f"attempting connection to ({self.host}, {self.port})")
                self.client.connect(self.host, self.port)
                self.client.packet_callback = self.handle_packet
                self.client.listen_for_packets()
            except:
                pass

    def handle_packet(self, data):
        self.received_packet.emit(data)


class AdministratorControlPanel(QWidget):

    def __init__(self, function_classes):
        super().__init__()
        self.client = RATClient()
        self.registry = RATFunctionRegistry()
        self.function_uis = []

        for function_class in function_classes:
            self.registry.add_function(function_class(Side.ADMIN_SIDE, self.client.packet_queue))

        self.setWindowTitle('Administrator Control Panel')
        self.setGeometry(100, 100, 400, 300)

        self.setup_echo()

        # create a network thread and start it
        self.network_thread = AdminNetworkThread(self.client, "localhost", 8888, parent=self)
        self.network_thread.received_packet.connect(self.gui_handle_packet)
        self.network_thread.start()

    def setup_echo(self):
        self.echo_button = QPushButton('Echo', self)
        self.echo_button.move(100, 100)
        self.echo_button.resize(200, 30)
        self.echo_ui = EchoUI(self.registry.get_function(1))
        self.echo_button.clicked.connect(self.echo_ui.show)

    def gui_handle_packet(self, data):
        self.registry.route_packet(data)
