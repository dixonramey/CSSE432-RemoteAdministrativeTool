import struct
import pyautogui

from RATFunction.RATFunction import RATFunction


class Message(RATFunction):

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)
        self.received_echo_callback = lambda echo_str: ()

    def handle_packet_admin_side(self, data):
        packet_id, echo_str = struct.unpack("I 2044s", data)
        self.received_echo_callback(echo_str.decode())

    def handle_packet_remote_side(self, data):
        packet_id, echo_str = struct.unpack("I 2044s", data)
        echo_str = echo_str.decode().rstrip('\0')
        pyautogui.alert(echo_str, 'Alert')

    def identifier(self) -> int:
        return 1

    def send_message(self, text):
        self.packet_queue.put(struct.pack("I 2044s", self.identifier(), text.encode()))
