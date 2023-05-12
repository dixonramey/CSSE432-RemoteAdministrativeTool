import struct
import pyautogui

from Constants import PACKET_SIZE
from RATFunction.RATFunction import RATFunction


class Message(RATFunction):

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)
        self.received_echo_callback = lambda echo_str: ()

    def handle_packet_admin_side(self, data):
        pass

    def handle_packet_remote_side(self, data):
        packet_id, message_str = struct.unpack(f"I {PACKET_SIZE - 4}s", data)
        message_str = message_str.decode().rstrip('\0')
        pyautogui.alert(message_str, 'Alert')

    def identifier(self) -> int:
        return 1

    def send_message(self, text):
        self.packet_queue.put(struct.pack(f"I {PACKET_SIZE - 4}s", self.identifier(), text.encode()))
