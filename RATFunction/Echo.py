import struct

from RATFunction.RATFunction import RATFunction


class Echo(RATFunction):

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)
        self.received_echo_callback = lambda echo_str: ()

    def handle_packet_admin_side(self, data):
        packet_id, echo_str = struct.unpack("I 2044s", data)
        self.received_echo_callback(echo_str.decode())

    def handle_packet_remote_side(self, data):
        packet_id, echo_str = struct.unpack("I 2044s", data)
        echo_str = echo_str.decode()
        print(echo_str)
        return_packet = struct.pack("I 2044s", self.identifier(), echo_str.upper().encode())
        self.packet_queue.put(return_packet)

    def identifier(self) -> int:
        return 1

    def send_echo(self, text):
        self.packet_queue.put(struct.pack("I 2044s", self.identifier(), text.encode()))
