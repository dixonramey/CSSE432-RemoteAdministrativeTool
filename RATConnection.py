import queue
import socket
from threading import Thread
from abc import ABC


class RATConnection(ABC):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.packet_callback = lambda data: ()
        self.packet_queue = queue.Queue()
        Thread(target=self._packet_loop, daemon=True).start()

    def send_packet(self, buffer):
        self.packet_queue.put(buffer)

    def _packet_loop(self):
        while True:
            buffer = self.packet_queue.get()
            self.socket.send(buffer)

    def listen_for_packets(self):
        while True:
            data = self.socket.recv(2048)
            if data and len(data) >= 2:
                self.packet_callback(data)


class RATClient(RATConnection):
    def connect(self, host, port):
        self.socket.connect((host, port))


class RATServer(RATConnection):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.client_address = None

    def listen(self, port):
        self.socket.bind(("localhost", port))
        self.socket.listen(1)
        self.socket, self.client_address = self.socket.accept()
