import sys
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton

from RATConnection import RATClient


class AdministratorMode(object):
    def __init__(self):
        pass

    def start(self):
        pass

class NetworkThread(QThread):
    received_data = pyqtSignal(bytes)

    def __init__(self, client: RATClient, host, port, parent=None):
        super().__init__(parent)
        self.client = client
        self.host = host
        self.port = port

    def run(self):
        print("running network thread")
        self.client.connect(self.host, 8888)
        self.client.packet_callback = self.handle_packet
        self.client.listen_for_packets()

    def handle_packet(self, b):
        print(b.decode())
        self.received_data.emit(b)


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Asynchronous TCP Packet Updates')
        self.setGeometry(100, 100, 400, 300)

        # create a label to display the received data
        self.label = QLabel(self)
        self.label.move(50, 50)
        self.label.resize(300, 30)

        # create a button to execute a function
        self.button = QPushButton('Client Send Packet', self)
        self.button.move(50, 100)
        self.button.resize(200, 30)
        self.button.clicked.connect(self.send_packet)

        # create a network thread and start it
        self.client = RATClient()
        self.network_thread = NetworkThread(self.client, "localhost", 8888, parent=self)
        self.network_thread.received_data.connect(self.update_gui)
        self.network_thread.start()

    def update_gui(self, data):
        # update the GUI with the received data
        self.label.setText(data.decode())

    def send_packet(self):
        self.client.send_packet(b"hello world")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())
